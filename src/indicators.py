# src/indicators.py
"""
indicators.py — 기술 지표 계산

Indicators 클래스 (모두 @staticmethod):
- calc_rsi: RSI(14일, Wilder EWM 방식)
- detect_cross_signal: 골든크로스/데드크로스 감지 (최근 5거래일 내 교차)
- calc_volume_ratio: 당일 거래량 / 20일 평균 거래량
- get_signal_badge: UI 배지 정보 반환
"""
import pandas as pd
import numpy as np


class Indicators:

    @staticmethod
    def calc_rsi(prices: pd.Series, period: int = 14) -> float:
        """RSI 계산 (Wilder EWM 방식)

        Args:
            prices: 종가 시계열
            period: RSI 기간 (기본 14일)

        Returns:
            최신 RSI 값 (0~100), 데이터 부족 시 50.0 반환
        """
        if len(prices) < period + 1:
            return 50.0

        delta = prices.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        # Wilder smoothing = EWM with alpha = 1/period
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()

        # avg_loss가 0이면 RSI = 100
        last_loss = avg_loss.iloc[-1]
        if last_loss < 1e-10:
            return 100.0

        rs = avg_gain.iloc[-1] / last_loss
        rsi = 100 - (100 / (1 + rs))
        return round(float(rsi), 1)

    @staticmethod
    def detect_cross_signal(
        df: pd.DataFrame,
        short: int = 5,
        long: int = 20,
        lookback: int = 5,
    ) -> str:
        """골든크로스/데드크로스 감지

        최근 `lookback` 거래일 내에 단기 이동평균선이 장기 이동평균선을
        위로(골든크로스) 또는 아래로(데드크로스) 교차했는지 감지한다.

        Args:
            df: "Close" 컬럼을 포함하는 DataFrame
            short: 단기 이동평균 기간 (기본 5일)
            long: 장기 이동평균 기간 (기본 20일)
            lookback: 교차 감지 범위 거래일 수 (기본 5일)

        Returns:
            "golden_cross" | "dead_cross" | "above" | "below" | "neutral"
        """
        if len(df) < long + lookback:
            return "neutral"

        close = df["Close"]
        ma_short = close.rolling(short).mean()
        ma_long = close.rolling(long).mean()

        # 최근 lookback일 내 교차 감지
        # i=1: 오늘(iloc[-1]) vs 어제(iloc[-2]) 비교
        # i=2: 어제(iloc[-2]) vs 그제(iloc[-3]) 비교, ...
        # prev_diff = i+1일 전, curr_diff = i일 전 (최신→과거 방향)
        for i in range(1, lookback + 1):
            if len(ma_short) < i + 1:
                break
            prev_diff = ma_short.iloc[-(i + 1)] - ma_long.iloc[-(i + 1)]
            curr_diff = ma_short.iloc[-i] - ma_long.iloc[-i]

            if pd.isna(prev_diff) or pd.isna(curr_diff):
                continue

            if prev_diff < 0 and curr_diff >= 0:
                return "golden_cross"
            if prev_diff > 0 and curr_diff <= 0:
                return "dead_cross"

        # 교차 없음 → 현재 배치 반환
        curr = ma_short.iloc[-1] - ma_long.iloc[-1]
        if pd.isna(curr):
            return "neutral"
        return "above" if curr > 0 else "below"

    @staticmethod
    def calc_volume_ratio(df: pd.DataFrame, period: int = 20) -> float:
        """당일 거래량 / 최근 N일 평균 거래량

        Args:
            df: "Volume" 컬럼을 포함하는 DataFrame
            period: 평균 계산 기간 (기본 20일)

        Returns:
            거래량 비율 (1.0 = 평균과 동일), 계산 불가 시 1.0
        """
        if len(df) < 2 or "Volume" not in df.columns:
            return 1.0

        # 당일(iloc[-1]) 제외한 직전 period일 평균
        avg_vol = df["Volume"].iloc[-(period + 1):-1].mean()
        if avg_vol == 0 or pd.isna(avg_vol):
            return 1.0

        ratio = df["Volume"].iloc[-1] / avg_vol
        return round(float(ratio), 2)

    @staticmethod
    def get_signal_badge(cross: str, rsi: float, vol_ratio: float) -> dict:
        """UI 표시용 신호 배지 정보 반환

        우선순위: 골든/데드크로스 > RSI 과열/과매도 > 상승/하락배치 > 중립

        Returns:
            {"label": str, "emoji": str, "cls": str}
        """
        if cross == "golden_cross":
            return {"label": "골든크로스", "emoji": "🟢", "cls": "badge-golden"}
        if cross == "dead_cross":
            return {"label": "데드크로스", "emoji": "🔴", "cls": "badge-dead"}
        if rsi > 70:
            return {"label": "과열", "emoji": "🔥", "cls": "badge-hot"}
        if rsi < 30:
            return {"label": "과매도", "emoji": "❄", "cls": "badge-cold"}
        if cross == "above":
            return {"label": "상승배치", "emoji": "📈", "cls": "badge-up"}
        if cross == "below":
            return {"label": "하락배치", "emoji": "📉", "cls": "badge-down"}
        return {"label": "중립", "emoji": "➡", "cls": "badge-neutral"}
