# tests/test_data_fetcher.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.data_fetcher import DataFetcher


def test_fetch_market_data_returns_dataframe():
    """KRX API는 환경에 따라 차단될 수 있으므로 pykrx 호출을 mock으로 처리."""
    fetcher = DataFetcher()

    # 샘플 OHLCV 데이터 (pykrx get_market_ohlcv 반환 형식 모사)
    sample_ohlcv = pd.DataFrame(
        {"시가": [70000], "고가": [71000], "저가": [69000], "종가": [70500], "거래량": [1000000], "등락률": [0.7]},
        index=pd.Index(["005930"], name="티커"),
    )
    # 샘플 시가총액 데이터
    sample_cap = pd.DataFrame(
        {"시가총액": [420_000_000_000_000]},
        index=pd.Index(["005930"], name="티커"),
    )

    with patch("src.data_fetcher.stock.get_market_ohlcv", return_value=sample_ohlcv), \
         patch("src.data_fetcher.stock.get_market_cap", return_value=sample_cap):
        df = fetcher.fetch_market_data("20260307")

    assert df is not None
    assert len(df) > 0
    # 등락률 컬럼 존재 확인
    assert "등락률" in df.columns


def test_fetch_etf_history_returns_enough_rows():
    fetcher = DataFetcher()
    # KODEX 반도체 (091160)
    df = fetcher.fetch_etf_history("091160", days=70)
    assert df is not None
    assert len(df) >= 60  # 60일선 계산을 위해 최소 60개


def test_fetch_stock_returns_daily():
    fetcher = DataFetcher()
    # 삼성전자 일간 수익률
    result = fetcher.fetch_stock_returns("005930", period="daily")
    assert "return_pct" in result
    assert isinstance(result["return_pct"], float)


def test_fetch_stock_returns_weekly():
    fetcher = DataFetcher()
    result = fetcher.fetch_stock_returns("005930", period="weekly")
    assert "return_pct" in result


def test_fetch_stock_returns_monthly():
    fetcher = DataFetcher()
    result = fetcher.fetch_stock_returns("005930", period="monthly")
    assert "return_pct" in result
