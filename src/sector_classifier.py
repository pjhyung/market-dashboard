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
from src.sector_config import SECTORS, MANUAL_MAPPING


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
            raw_change = row.get("등락률", 0)
            change = float(raw_change if pd.notna(raw_change) else 0)

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

        # 반환 전 내부 계산 상태 제거
        for sd in active.values():
            sd.pop("weighted_sum", None)

        sorted_sectors = sorted(
            active.items(),
            key=lambda x: x[1]["change_pct"],
            reverse=True,
        )
        return dict(sorted_sectors[:10])
