# tests/test_indicators.py
import pandas as pd
import numpy as np
import pytest
from src.indicators import Indicators


def make_df(closes, volumes=None):
    """테스트용 DataFrame 생성"""
    if volumes is None:
        volumes = [1000] * len(closes)
    return pd.DataFrame({"Close": closes, "Volume": volumes}, dtype=float)


def test_rsi_overbought():
    """계속 상승하는 가격 → RSI > 70"""
    df = make_df([100 + i * 2 for i in range(20)])
    rsi = Indicators.calc_rsi(df["Close"])
    assert rsi > 70, f"과매수 구간에서 RSI가 {rsi}로 70 미만"


def test_rsi_oversold():
    """계속 하락하는 가격 → RSI < 30"""
    df = make_df([100 - i * 2 for i in range(20)])
    rsi = Indicators.calc_rsi(df["Close"])
    assert rsi < 30, f"과매도 구간에서 RSI가 {rsi}로 30 초과"


def test_rsi_neutral():
    """오르내림 반복 → RSI 30~70 사이"""
    prices = [100, 102, 99, 103, 100, 102, 99, 103, 100, 102,
              99, 103, 100, 102, 99, 103, 100, 102, 99, 103]
    df = make_df(prices)
    rsi = Indicators.calc_rsi(df["Close"])
    assert 30 <= rsi <= 70, f"중립 구간에서 RSI가 {rsi}로 범위 벗어남"


def test_golden_cross_detected():
    """단기선이 장기선을 위로 교차하면 golden_cross 반환"""
    # 처음 20개는 하락(단기 < 장기), 이후 5개 급등(단기 > 장기)
    prices = [100 - i * 0.5 for i in range(20)] + [120, 125, 130, 135, 140]
    df = make_df(prices)
    signal = Indicators.detect_cross_signal(df, short=5, long=20)
    assert signal == "golden_cross", f"골든크로스 미감지: {signal}"


def test_dead_cross_detected():
    """단기선이 장기선을 아래로 교차하면 dead_cross 반환"""
    # 처음 20개는 상승(단기 > 장기), 이후 5개 급락(단기 < 장기)
    prices = [100 + i * 0.5 for i in range(20)] + [80, 75, 70, 65, 60]
    df = make_df(prices)
    signal = Indicators.detect_cross_signal(df, short=5, long=20)
    assert signal == "dead_cross", f"데드크로스 미감지: {signal}"


def test_volume_ratio_surge():
    """당일 거래량이 평균의 5배 → ratio > 3"""
    volumes = [1000] * 19 + [5000]
    df = make_df([100] * 20, volumes=volumes)
    ratio = Indicators.calc_volume_ratio(df)
    assert ratio > 3.0, f"거래량 급증 미감지: {ratio}"


def test_volume_ratio_normal():
    """모든 거래량이 동일하면 ratio ≈ 1.0"""
    df = make_df([100] * 20, volumes=[1000] * 20)
    ratio = Indicators.calc_volume_ratio(df)
    assert 0.9 <= ratio <= 1.1, f"정상 거래량에서 ratio가 {ratio}"


def test_signal_badge_golden_cross():
    badge = Indicators.get_signal_badge("golden_cross", 55.0, 1.2)
    assert badge["cls"] == "badge-golden"
    assert "골든크로스" in badge["label"]


def test_signal_badge_dead_cross():
    badge = Indicators.get_signal_badge("dead_cross", 45.0, 1.0)
    assert badge["cls"] == "badge-dead"


def test_signal_badge_hot():
    badge = Indicators.get_signal_badge("above", 75.0, 1.5)
    assert badge["cls"] == "badge-hot"


def test_signal_badge_cold():
    badge = Indicators.get_signal_badge("below", 25.0, 0.8)
    assert badge["cls"] == "badge-cold"
