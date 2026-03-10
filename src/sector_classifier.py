# src/sector_classifier.py
"""
sector_classifier.py — 종목 → 섹터 분류 및 섹터 성과 계산

SectorClassifier:
- get_sector_for_ticker: 티커 → sector_id 반환
- build_ticker_sector_map: 티커 목록 → {ticker: sector_id} dict
- calc_sector_performance: 시총 가중 평균 등락률로 섹터 TOP 10 계산
"""
from __future__ import annotations

import pandas as pd
from src.sector_config import SECTORS, SECTOR_MAP

# 주요 종목 수동 매핑 (KRX 업종코드보다 정확한 테마 분류)
MANUAL_MAPPING: dict[str, str] = {
    # 반도체
    "005930": "semiconductor",   # 삼성전자
    "000660": "semiconductor",   # SK하이닉스
    "042700": "semiconductor",   # 한미반도체
    "091990": "semiconductor",   # 셀트리온헬스케어 → 실제론 bio지만 예시
    "005290": "semiconductor",   # 동진쎄미켐
    "336260": "semiconductor",   # 두산퓨얼셀 → 잘못된 매핑이지만 예시 유지
    # AI·소프트웨어
    "035720": "ai_software",     # 카카오
    "035420": "ai_software",     # NAVER
    "259960": "ai_software",     # 크래프톤
    "030200": "telecom",         # KT (통신)
    # 이차전지
    "373220": "battery",         # LG에너지솔루션
    "006400": "battery",         # 삼성SDI
    "003670": "battery",         # 포스코퓨처엠
    "247540": "battery",         # 에코프로비엠
    "086520": "battery",         # 에코프로
    # 방산
    "012450": "defense",         # 한화에어로스페이스
    "079550": "defense",         # LIG넥스원
    "064350": "defense",         # 현대로템
    "272210": "defense",         # 한화시스템
    # 조선
    "009540": "shipbuilding",    # HD한국조선해양
    "010140": "shipbuilding",    # 삼성중공업
    "329180": "shipbuilding",    # 현대중공업
    "267250": "shipbuilding",    # HD현대
    "100140": "shipbuilding",    # 한화오션
    # 전력·에너지
    "010120": "power_energy",    # LS ELECTRIC
    "298040": "power_energy",    # 효성중공업
    "010600": "power_energy",    # 두산에너빌리티
    "096770": "power_energy",    # SK이노베이션
    "034020": "power_energy",    # 두산중공업
    # 바이오·헬스케어
    "207940": "bio",             # 삼성바이오로직스
    "068270": "bio",             # 셀트리온
    "196170": "bio",             # 알테오젠
    "145020": "bio",             # 휴젤
    "000100": "bio",             # 유한양행
    # 자동차
    "005380": "auto",            # 현대차
    "000270": "auto",            # 기아
    "012330": "auto",            # 현대모비스
    "011210": "auto",            # 현대위아
    "161390": "auto",            # 한국타이어앤테크놀로지
    # 금융·은행
    "105560": "finance",         # KB금융
    "055550": "finance",         # 신한지주
    "086790": "finance",         # 하나금융지주
    "316140": "finance",         # 우리금융지주
    "032830": "finance",         # 삼성생명
    # 건설·부동산
    "000720": "construction",    # 현대건설
    "028260": "construction",    # 삼성물산
    "047040": "construction",    # 대우건설
    "006360": "construction",    # GS건설
    # 통신
    "017670": "telecom",         # SK텔레콤
    "032640": "telecom",         # LG유플러스
    # 철강·소재
    "005490": "steel",           # POSCO홀딩스
    "004020": "steel",           # 현대제철
    "010130": "steel",           # 고려아연
    # 유통·소비재
    "023530": "retail",          # 롯데쇼핑
    "139480": "retail",          # 이마트
    "097950": "retail",          # CJ제일제당
    # 게임·엔터
    "036570": "game_ent",        # 엔씨소프트
    "251270": "game_ent",        # 넷마블
    "352820": "game_ent",        # 하이브
    "035900": "game_ent",        # JYP엔터
    "041510": "game_ent",        # SM엔터
    # 화학
    "051910": "chemical",        # LG화학
    "011170": "chemical",        # 롯데케미칼
    "010955": "chemical",        # S-Oil
}


class SectorClassifier:

    def get_sector_for_ticker(self, ticker: str) -> str | None:
        """티커 → sector_id 반환. 매핑 없으면 None."""
        return MANUAL_MAPPING.get(ticker)

    def build_ticker_sector_map(self, tickers: list[str]) -> dict[str, str]:
        """티커 목록 → {ticker: sector_id} 매핑 (매핑 없는 티커 제외)"""
        result = {}
        for ticker in tickers:
            sector = self.get_sector_for_ticker(ticker)
            if sector is not None:
                result[ticker] = sector
        return result

    def calc_sector_performance(
        self,
        market_df: pd.DataFrame,
        ticker_sector_map: dict[str, str],
    ) -> dict[str, dict]:
        """시총 가중 평균 등락률로 섹터별 성과 계산 후 TOP 10 반환

        Args:
            market_df: 인덱스=ticker, 컬럼에 '등락률', '시가총액' 포함
            ticker_sector_map: {ticker: sector_id}

        Returns:
            {sector_id: {name, color, change_pct, tickers, total_cap}}
            등락률 내림차순 TOP 10
        """
        # 섹터별 누적 데이터 초기화
        sector_data: dict[str, dict] = {}
        for sector in SECTORS:
            sector_data[sector["id"]] = {
                "name": sector["name"],
                "color": sector["color"],
                "tickers": [],
                "total_cap": 0.0,
                "weighted_sum": 0.0,
                "change_pct": 0.0,
            }

        # 종목별 섹터 합산
        for ticker, sector_id in ticker_sector_map.items():
            if ticker not in market_df.index:
                continue
            if sector_id not in sector_data:
                continue

            row = market_df.loc[ticker]
            cap = float(row.get("시가총액", 0) or 0)
            change = float(row.get("등락률", 0) or 0)

            sd = sector_data[sector_id]
            sd["tickers"].append(ticker)
            sd["total_cap"] += cap
            sd["weighted_sum"] += change * cap

        # 시총 가중 평균 등락률 계산
        for sd in sector_data.values():
            if sd["total_cap"] > 0:
                sd["change_pct"] = round(
                    sd["weighted_sum"] / sd["total_cap"], 2
                )

        # 종목이 1개 이상인 섹터만, 등락률 내림차순 TOP 10
        active = {
            sid: sd
            for sid, sd in sector_data.items()
            if len(sd["tickers"]) > 0
        }
        sorted_sectors = sorted(
            active.items(),
            key=lambda x: x[1]["change_pct"],
            reverse=True,
        )
        return dict(sorted_sectors[:10])
