# tests/test_sector_classifier.py
import pandas as pd
import pytest
from src.sector_classifier import SectorClassifier


def test_manual_mapping_semiconductor():
    """삼성전자(005930) → semiconductor 섹터"""
    clf = SectorClassifier()
    assert clf.get_sector_for_ticker("005930") == "semiconductor"


def test_manual_mapping_defense():
    """한화에어로스페이스(012450) → defense 섹터"""
    clf = SectorClassifier()
    assert clf.get_sector_for_ticker("012450") == "defense"


def test_unknown_ticker_returns_none():
    """매핑 없는 티커 → None"""
    clf = SectorClassifier()
    assert clf.get_sector_for_ticker("999999") is None


def test_build_ticker_sector_map():
    """티커 목록 → {ticker: sector_id} 매핑 (매핑 없는 티커 제외)"""
    clf = SectorClassifier()
    tickers = ["005930", "012450", "999999"]
    result = clf.build_ticker_sector_map(tickers)
    assert result["005930"] == "semiconductor"
    assert result["012450"] == "defense"
    assert "999999" not in result


def test_calc_sector_performance_weighted():
    """시가총액 가중 평균 등락률 계산"""
    clf = SectorClassifier()
    market_df = pd.DataFrame({
        "등락률": [10.0, 2.0, 5.0],
        "시가총액": [2000.0, 1000.0, 500.0],
    }, index=["005930", "000660", "012450"])

    ticker_sector_map = {
        "005930": "semiconductor",
        "000660": "semiconductor",
        "012450": "defense",
    }

    result = clf.calc_sector_performance(market_df, ticker_sector_map)

    # 반도체: (10*2000 + 2*1000) / 3000 = 22000/3000 = 7.33%
    assert "semiconductor" in result
    assert abs(result["semiconductor"]["change_pct"] - 7.33) < 0.1

    # 방산: (5*500) / 500 = 5.0%
    assert "defense" in result
    assert abs(result["defense"]["change_pct"] - 5.0) < 0.1


def test_calc_sector_performance_top10():
    """결과가 최대 10개 섹터만 반환 (등락률 내림차순)"""
    clf = SectorClassifier()
    # 15개 섹터 모두 있는 상황을 시뮬레이션
    from src.sector_config import SECTORS, MANUAL_MAPPING

    # MANUAL_MAPPING에서 15개 섹터 종목들 가져오기
    sample_tickers = list(MANUAL_MAPPING.keys())[:15]
    sector_map = {t: MANUAL_MAPPING[t] for t in sample_tickers}

    market_data = {
        "등락률": [float(i) for i in range(len(sample_tickers))],
        "시가총액": [1000.0] * len(sample_tickers),
    }
    market_df = pd.DataFrame(market_data, index=sample_tickers)

    result = clf.calc_sector_performance(market_df, sector_map)
    assert len(result) <= 10


def test_calc_sector_performance_empty_df():
    """빈 market_df → 빈 dict 반환"""
    clf = SectorClassifier()
    result = clf.calc_sector_performance(pd.DataFrame(), {})
    assert result == {}


def test_calc_sector_performance_excludes_weighted_sum():
    """반환값에 내부 계산 상태(weighted_sum)가 없어야 함"""
    clf = SectorClassifier()
    market_df = pd.DataFrame({
        "등락률": [5.0],
        "시가총액": [1000.0],
    }, index=["005930"])
    result = clf.calc_sector_performance(market_df, {"005930": "semiconductor"})
    assert "weighted_sum" not in result["semiconductor"]


def test_calc_sector_performance_sorted_descending():
    """결과가 등락률 내림차순으로 정렬돼야 함"""
    clf = SectorClassifier()
    market_df = pd.DataFrame({
        "등락률": [5.0, 2.0],
        "시가총액": [1000.0, 1000.0],
    }, index=["005930", "012450"])
    result = clf.calc_sector_performance(
        market_df,
        {"005930": "semiconductor", "012450": "defense"}
    )
    sectors = list(result.values())
    assert sectors[0]["change_pct"] >= sectors[1]["change_pct"]
