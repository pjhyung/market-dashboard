# src/ai_analyst.py
"""
ai_analyst.py — Claude CLI subprocess 기반 AI 시장 분석

claude --print 명령에 프롬프트를 stdin으로 전달해 분석 텍스트를 받는다.
Claude Pro 구독 토큰을 사용하므로 API 키 불필요.

주의: claude CLI가 설치·로그인된 환경에서만 동작함.
"""
import subprocess


class AIAnalyst:

    def _run_claude(self, prompt: str, timeout: int = 120) -> str:
        """Claude CLI subprocess 실행 공통 메서드

        Args:
            prompt: stdin으로 전달할 프롬프트 텍스트
            timeout: 최대 대기 시간 (초)

        Returns:
            Claude 응답 텍스트. 실패 시 빈 문자열.
        """
        try:
            result = subprocess.run(
                ["claude", "--print"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout,
            )
            if result.returncode != 0:
                print(f"  [경고] Claude CLI 오류 (code {result.returncode}): {result.stderr[:200]}")
                return ""
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"  [경고] Claude CLI 타임아웃 ({timeout}초 초과)")
            return ""
        except FileNotFoundError:
            print("  [경고] claude CLI를 찾을 수 없음. 설치 및 로그인 확인 필요.")
            return ""
        except Exception as e:
            print(f"  [경고] Claude CLI 실행 실패: {e}")
            return ""

    def analyze_sector(self, sector_data: dict, top5: list) -> str:
        """섹터 AI 코멘트 생성 (2-3문장)

        Args:
            sector_data: 섹터 정보 dict (name, change_pct, rsi, volume_ratio, signal_badge)
            top5: 종목 TOP 5 리스트 [{"name": str, "return_pct": float}]

        Returns:
            2-3문장 분석 텍스트. 실패 시 기본 텍스트.
        """
        signal_label = sector_data.get("signal_badge", {}).get("label", "중립")
        top5_text = ", ".join(
            f"{s['name']} {s['return_pct']:+.1f}%"
            for s in top5
        ) if top5 else "데이터 없음"

        prompt = f"""당신은 국내 주식 시장 분석 전문가입니다.
아래 섹터 데이터를 보고 투자자 관점에서 핵심만 2-3문장으로 분석해주세요.
전문 용어를 쓰되 쉽게 설명하고, 수치를 직접 인용하세요.
마크다운 없이 순수 텍스트로만 답변하세요.

섹터: {sector_data.get('name', '')}
당일 등락율: {sector_data.get('change_pct', 0):+.2f}%
기술 신호: {signal_label}
RSI: {sector_data.get('rsi', 'N/A')}
거래량 비율: {sector_data.get('volume_ratio', 1.0):.1f}배
주도 종목 TOP5: {top5_text}

분석 (2-3문장, 마크다운 없이):"""

        response = self._run_claude(prompt, timeout=120)
        if not response:
            return f"{sector_data.get('name', '')} 섹터 AI 분석을 불러올 수 없습니다."
        return response

    def analyze_market_summary(self, top10_sectors: list) -> str:
        """전체 시장 종합 분석 (3-4문장)

        Args:
            top10_sectors: 섹터 데이터 dict 리스트 (TOP 10)

        Returns:
            3-4문장 종합 분석 텍스트. 실패 시 기본 텍스트.
        """
        sector_lines = "\n".join(
            f"- {s.get('name', '')}: {s.get('change_pct', 0):+.2f}%"
            f" ({s.get('signal_badge', {}).get('label', '중립')})"
            for s in top10_sectors
        )

        prompt = f"""국내 주식 시장 오늘의 종합 분석을 해주세요.
마크다운 없이 순수 텍스트로만 답변하세요.

주도 섹터 TOP 10:
{sector_lines}

다음 내용을 포함해 3-4문장으로 작성:
1. 오늘 시장의 전반적 흐름
2. 가장 주목할 섹터와 이유
3. 투자자가 주의할 점

종합 분석 (3-4문장, 마크다운 없이):"""

        response = self._run_claude(prompt, timeout=180)
        if not response:
            return "시장 종합 분석을 불러올 수 없습니다."
        return response
