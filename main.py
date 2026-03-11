# main.py
"""
main.py — Korea Market Command 진입점

실행: python main.py
  1. pykrx + FDR로 당일 시장 데이터 수집
  2. 섹터별 성과 계산 → TOP 10
  3. ETF 기술 지표 계산 (RSI, 크로스, 거래량)
  4. 섹터별 TOP 5 종목 수집 (일/주/월)
  5. Claude CLI로 AI 분석 생성
  6. JSON + HTML 생성 → git push
"""
import json
import os
import subprocess
import sys
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.data_fetcher import DataFetcher
from src.indicators import Indicators
from src.sector_classifier import SectorClassifier
from src.sector_config import SECTORS, SECTOR_MAP, MANUAL_MAPPING
from src.ai_analyst import AIAnalyst


def get_top5_for_sector(
    sector_id: str,
    ticker_sector_map: dict,
    market_df,
    fetcher: DataFetcher,
    period: str,
) -> list:
    """특정 섹터의 당일 상승률 상위 5개 종목 반환

    시가총액 상위 종목 위주로 조회해 API 호출 수를 제한한다.
    """
    from pykrx import stock as pykrx_stock

    sector_tickers = [t for t, s in ticker_sector_map.items() if s == sector_id]
    if not sector_tickers:
        return []

    # 시가총액 기준 상위 30개만 조회 (성능)
    if "시가총액" in market_df.columns:
        caps = market_df.loc[
            market_df.index.isin(sector_tickers), "시가총액"
        ].sort_values(ascending=False)
        sector_tickers = list(caps.index[:30])
    else:
        sector_tickers = sector_tickers[:30]

    results = []
    for ticker in sector_tickers:
        try:
            ret = fetcher.fetch_stock_returns(ticker, period)
            name = pykrx_stock.get_market_ticker_name(ticker)
            results.append({
                "ticker": ticker,
                "name": name,
                "return_pct": ret["return_pct"],
            })
        except Exception:
            pass

    results.sort(key=lambda x: x["return_pct"], reverse=True)
    return results[:5]


def build_jinja_env() -> Environment:
    """ensure_ascii=False 적용된 Jinja2 환경 생성"""
    env = Environment(loader=FileSystemLoader("templates"))
    env.policies["json.dumps_kwargs"] = {"ensure_ascii": False}
    return env


def main():
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    date_key = today.strftime("%Y%m%d")

    print(f"\n{'='*55}")
    print(f"  Korea Market Command — {date_str}")
    print(f"{'='*55}\n")

    fetcher = DataFetcher()
    clf = SectorClassifier()
    analyst = AIAnalyst()
    env = build_jinja_env()

    # 1. 시장 데이터 수집
    print("[1/6] 시장 데이터 수집 중...")
    market_df = fetcher.fetch_market_data(date_key)
    if market_df.empty:
        print(f"  [오류] {date_key} 시장 데이터 없음. 휴장일이거나 데이터 지연일 수 있음.")
        sys.exit(1)
    print(f"  수집 완료: {len(market_df)}개 종목")

    # 2. 섹터 분류 + 성과 계산
    print("[2/6] 섹터 분류 중...")
    all_tickers = list(market_df.index)
    ticker_sector_map = clf.build_ticker_sector_map(all_tickers)
    top10 = clf.calc_sector_performance(market_df, ticker_sector_map)
    print(f"  주도 섹터 {len(top10)}개 추출")

    # 3. ETF 기술 지표 + TOP5 수집
    print("[3/6] ETF 기술 지표 + 종목 TOP5 수집 중...")
    sectors_data = []
    for rank, (sector_id, sd) in enumerate(top10.items(), 1):
        sector_cfg = SECTOR_MAP.get(sector_id, {})
        etf_ticker = sector_cfg.get("etf_ticker")

        # ETF 기술 지표
        rsi, cross, vol_ratio, ma5, ma20 = 50.0, "neutral", 1.0, None, None
        if etf_ticker:
            try:
                etf_df = fetcher.fetch_etf_history(etf_ticker, days=70)
                if not etf_df.empty and len(etf_df) >= 20:
                    rsi = Indicators.calc_rsi(etf_df["Close"])
                    cross = Indicators.detect_cross_signal(etf_df)
                    vol_ratio = Indicators.calc_volume_ratio(etf_df)
                    ma5 = float(etf_df["Close"].rolling(5).mean().iloc[-1])
                    ma20 = float(etf_df["Close"].rolling(20).mean().iloc[-1])
            except Exception as e:
                print(f"  [{sector_id}] ETF 지표 계산 실패: {e}")

        badge = Indicators.get_signal_badge(cross, rsi, vol_ratio)

        # TOP5 (일/주/월)
        print(f"  [{rank:02d}] {sd['name']} TOP5 수집 중...")
        top5 = {}
        for period in ["daily", "weekly", "monthly"]:
            top5[period] = get_top5_for_sector(
                sector_id, ticker_sector_map, market_df, fetcher, period
            )

        sectors_data.append({
            **sd,
            "id": sector_id,
            "color": sector_cfg.get("color", "#60A5FA"),
            "etf_name": sector_cfg.get("etf_name", ""),
            "rsi": rsi,
            "cross": cross,
            "volume_ratio": vol_ratio,
            "signal_badge": badge,
            "ma5": ma5,
            "ma20": ma20,
            "top5": top5,
            "ai_comment": "",
        })

    # 4. Claude AI 분석
    print("[4/6] Claude AI 분석 생성 중...")
    for sd in sectors_data:
        print(f"  [{sd['name']}] 분석 중...")
        sd["ai_comment"] = analyst.analyze_sector(sd, sd["top5"]["daily"])
    market_summary = analyst.analyze_market_summary(sectors_data)

    # 5. JSON + HTML 생성
    print("[5/6] HTML 생성 중...")
    os.makedirs("docs/data", exist_ok=True)

    # 날짜별 JSON 저장
    json_path = f"docs/data/{date_str}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "date": date_str,
            "sectors": sectors_data,
            "market_summary": market_summary,
        }, f, ensure_ascii=False, indent=2)

    # 이전/다음 날짜 계산
    existing = sorted([
        fn.replace(".json", "")
        for fn in os.listdir("docs/data")
        if fn.endswith(".json")
    ])
    idx = existing.index(date_str) if date_str in existing else -1
    prev_date = existing[idx - 1] if idx > 0 else None
    next_date = existing[idx + 1] if 0 <= idx < len(existing) - 1 else None

    # 날짜별 상세 HTML
    daily_tpl = env.get_template("daily.html.j2")
    daily_html = daily_tpl.render(
        date=date_str,
        sectors_data=sectors_data,
        market_summary=market_summary,
        prev_date=prev_date,
        next_date=next_date,
    )
    with open(f"docs/{date_str}.html", "w", encoding="utf-8") as f:
        f.write(daily_html)

    # 달력 데이터 구성 (전체 JSON 기반)
    calendar_data = {}
    for fn in sorted(os.listdir("docs/data")):
        if not fn.endswith(".json"):
            continue
        d = fn.replace(".json", "")
        try:
            with open(f"docs/data/{fn}", encoding="utf-8") as f:
                data = json.load(f)
            calendar_data[d] = {
                "sectors": [
                    {"name": s["name"], "color": s["color"]}
                    for s in data.get("sectors", [])[:5]
                ],
                "url": f"{d}.html",
            }
        except Exception as e:
            print(f"  [경고] {fn} 로드 실패: {e}")

    # 달력 메인 index.html
    cal_tpl = env.get_template("calendar.html.j2")
    cal_html = cal_tpl.render(
        year=today.year,
        month=today.month,
        calendar_data=calendar_data,
        last_updated=today.strftime("%Y-%m-%d %H:%M"),
    )
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(cal_html)

    print(f"  생성 완료: docs/{date_str}.html, docs/index.html")

    # 6. Git push
    print("[6/6] GitHub Pages 배포 중...")
    try:
        subprocess.run(["git", "add", "docs/"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"data: {date_str} 시장 데이터 업데이트"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        print(f"\n{'='*55}")
        print("  ✅ 배포 완료!")
        print(f"  https://<username>.github.io/market-dashboard/")
        print(f"{'='*55}\n")
    except subprocess.CalledProcessError as e:
        print(f"\n  [경고] git push 실패: {e}")
        print("  수동으로 git push를 실행해주세요.")


if __name__ == "__main__":
    main()
