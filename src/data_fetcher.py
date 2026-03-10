# src/data_fetcher.py
"""
data_fetcher.py — 국내 주식 데이터 수집

pykrx: 전 종목 OHLCV, 시가총액 (KRX 공식 데이터)
FinanceDataReader: ETF 가격 히스토리, 개별 종목 수익률 계산용
"""
from pykrx import stock
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta


class DataFetcher:
    def __init__(self):
        self.today = datetime.now().strftime("%Y%m%d")

    def fetch_market_data(self, date: str = None) -> pd.DataFrame:
        """KOSPI + KOSDAQ 전 종목 OHLCV + 시가총액 반환"""
        target = date or self.today
        try:
            print(f"  [데이터] {target} KOSPI 수집 중...")
            ohlcv_k = stock.get_market_ohlcv(target, market="KOSPI")
            cap_k = stock.get_market_cap(target, market="KOSPI")

            print(f"  [데이터] {target} KOSDAQ 수집 중...")
            ohlcv_q = stock.get_market_ohlcv(target, market="KOSDAQ")
            cap_q = stock.get_market_cap(target, market="KOSDAQ")

            df = pd.concat([ohlcv_k, ohlcv_q])
            cap_df = pd.concat([cap_k, cap_q])
            df = df.join(cap_df[["시가총액"]], how="left")
            df.index.name = "ticker"

            if df.empty:
                print(f"  [경고] {target} 시장 데이터 없음 (휴장일일 수 있음)")
            return df
        except Exception as e:
            print(f"  [오류] 시장 데이터 수집 실패 ({target}): {e}")
            return pd.DataFrame()

    def fetch_etf_history(self, ticker: str, days: int = 70) -> pd.DataFrame:
        """ETF 가격 히스토리 반환 (이동평균·RSI 계산용)

        Args:
            ticker: ETF 티커 (None이면 빈 DataFrame 반환)
            days: 가져올 최대 거래일 수
        """
        if ticker is None:
            return pd.DataFrame()

        end = datetime.now()
        # days * 2 달력일 조회 → tail(days)로 실제 필요 거래일 수 확보
        # (연간 거래일 약 250개 = 달력일 365일의 68%, days*2면 충분)
        start = end - timedelta(days=days * 2)
        try:
            df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"))
            return df.tail(days)
        except Exception as e:
            print(f"  [경고] ETF {ticker} 히스토리 조회 실패: {e}")
            return pd.DataFrame()

    def fetch_stock_returns(self, ticker: str, period: str = "daily") -> dict:
        """종목 수익률 계산 (daily / weekly / monthly)

        Returns:
            {"return_pct": float}  # 수익률 (%)
        """
        # 필요한 거래일 수 (여유분 2배)
        trading_days = {"daily": 1, "weekly": 5, "monthly": 21}
        fetch_days = {"daily": 10, "weekly": 30, "monthly": 60}
        n = trading_days.get(period, 1)

        end = datetime.now()
        start = end - timedelta(days=fetch_days.get(period, 10))

        try:
            df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"))
            if len(df) < 2:
                return {"return_pct": 0.0}

            actual_n = min(n, len(df) - 1)
            ret = (df["Close"].iloc[-1] / df["Close"].iloc[-1 - actual_n] - 1) * 100
            return {"return_pct": round(float(ret), 2)}
        except Exception as e:
            print(f"  [경고] {ticker} 수익률 조회 실패 ({period}): {e}")
            return {"return_pct": 0.0}

    def fetch_all_stock_names(self) -> dict:
        """전 종목 {ticker: 종목명} 매핑 반환 (인스턴스 캐시 사용)"""
        if hasattr(self, "_name_cache") and self._name_cache:
            return self._name_cache

        result = {}
        for market in ["KOSPI", "KOSDAQ"]:
            tickers = stock.get_market_ticker_list(market=market)
            for t in tickers:
                try:
                    result[t] = stock.get_market_ticker_name(t)
                except Exception:
                    pass
        self._name_cache = result
        return result
