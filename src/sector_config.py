# src/sector_config.py
"""
sector_config.py — 15개 테마 섹터 설정

SECTORS: 섹터 메타데이터 리스트 (id, name, color, etf, 업종코드, 키워드)
SECTOR_MAP: {sector_id: sector_dict} — O(1) 조회용
INDUSTRY_TO_SECTOR: {krx_업종코드: sector_id} — 종목→섹터 분류용
keywords: 뉴스·공시 텍스트 기반 보조 분류용 (현재 미사용, 향후 확장)
"""

# 섹터별 설정
SECTORS = [
    {
        "id": "semiconductor",
        "name": "반도체",
        "color": "#60A5FA",
        "etf_ticker": "091160",   # KODEX 반도체
        "etf_name": "KODEX 반도체",
        "krx_industry_codes": ["G251", "G252"],
        "keywords": ["반도체", "실리콘", "웨이퍼", "팹", "파운드리"],
    },
    {
        "id": "ai_software",
        "name": "AI·소프트웨어",
        "color": "#818CF8",
        "etf_ticker": "411030",   # KODEX K-AI
        "etf_name": "KODEX K-AI",
        "krx_industry_codes": ["J581", "J582"],
        "keywords": ["소프트웨어", "AI", "인공지능", "플랫폼", "클라우드"],
    },
    {
        "id": "battery",
        "name": "이차전지",
        "color": "#34D399",
        "etf_ticker": "305720",   # KODEX 2차전지산업
        "etf_name": "KODEX 2차전지산업",
        "krx_industry_codes": ["C280", "C291"],
        "keywords": ["배터리", "2차전지", "양극재", "음극재", "전해질", "분리막"],
    },
    {
        "id": "defense",
        "name": "방산",
        "color": "#F59E0B",
        "etf_ticker": "459580",   # KODEX K-방산&우주
        "etf_name": "KODEX K-방산&우주",
        "krx_industry_codes": ["C303"],
        "keywords": ["방산", "항공", "우주", "무기", "방어"],
    },
    {
        "id": "shipbuilding",
        "name": "조선",
        "color": "#A78BFA",
        "etf_ticker": "140710",   # KODEX 조선
        "etf_name": "KODEX 조선",
        "krx_industry_codes": ["C311"],
        "keywords": ["조선", "선박", "해양", "LNG선"],
    },
    {
        "id": "power_energy",
        "name": "전력·에너지",
        "color": "#F87171",
        "etf_ticker": "396520",   # KODEX K-신재생에너지
        "etf_name": "KODEX K-신재생에너지",
        "krx_industry_codes": ["D351", "D352", "C281"],
        "keywords": ["전력", "에너지", "변압기", "발전", "신재생", "태양광"],
    },
    {
        "id": "bio",
        "name": "바이오·헬스케어",
        "color": "#6EE7B7",
        "etf_ticker": "244580",   # KODEX 바이오
        "etf_name": "KODEX 바이오",
        "krx_industry_codes": ["C211", "Q861"],
        "keywords": ["바이오", "제약", "헬스케어", "신약", "백신"],
    },
    {
        "id": "auto",
        "name": "자동차",
        "color": "#FCD34D",
        "etf_ticker": "091180",   # KODEX 자동차
        "etf_name": "KODEX 자동차",
        "krx_industry_codes": ["C301"],
        "keywords": ["자동차", "전기차", "부품", "타이어"],
    },
    {
        "id": "finance",
        "name": "금융·은행",
        "color": "#93C5FD",
        "etf_ticker": "091220",   # KODEX 은행
        "etf_name": "KODEX 은행",
        "krx_industry_codes": ["K641", "K642", "K651"],
        "keywords": ["은행", "금융", "보험", "증권", "카드"],
    },
    {
        "id": "construction",
        "name": "건설·부동산",
        "color": "#C084FC",
        "etf_ticker": "134380",   # KODEX 건설
        "etf_name": "KODEX 건설",
        "krx_industry_codes": ["F411", "F412"],
        "keywords": ["건설", "부동산", "리츠", "플랜트"],
    },
    {
        "id": "telecom",
        "name": "통신",
        "color": "#67E8F9",
        "etf_ticker": "091230",   # KODEX 통신
        "etf_name": "KODEX 통신",
        "krx_industry_codes": ["J611", "J612"],
        "keywords": ["통신", "5G", "인터넷"],
    },
    {
        "id": "steel",
        "name": "철강·소재",
        "color": "#FB923C",
        "etf_ticker": "140700",   # KODEX 철강
        "etf_name": "KODEX 철강",
        "krx_industry_codes": ["C241", "C242", "C243"],
        "keywords": ["철강", "금속", "소재", "비철"],
    },
    {
        "id": "retail",
        "name": "유통·소비재",
        "color": "#A3E635",
        "etf_ticker": "266390",   # KODEX 경기소비재
        "etf_name": "KODEX 경기소비재",
        "krx_industry_codes": ["G471", "G472", "G461"],
        "keywords": ["유통", "소비재", "식품", "음료"],
    },
    {
        "id": "game_ent",
        "name": "게임·엔터",
        "color": "#F472B6",
        "etf_ticker": "364980",   # KODEX 게임&애니메이션
        "etf_name": "KODEX 게임&애니메이션",
        "krx_industry_codes": ["R901", "J591"],
        "keywords": ["게임", "엔터", "콘텐츠", "미디어", "엔터테인먼트"],
    },
    {
        "id": "chemical",
        "name": "화학",
        "color": "#E879F9",
        "etf_ticker": None,   # 화학 전용 ETF 없음, 지표 계산 생략
        "etf_name": "ETF 없음",
        "krx_industry_codes": ["C201", "C202", "C203"],
        "keywords": ["화학", "석유화학", "정유", "플라스틱"],
    },
]

# 섹터 ID로 빠르게 찾기
SECTOR_MAP = {s["id"]: s for s in SECTORS}

# 업종코드 → 섹터 ID 역매핑
INDUSTRY_TO_SECTOR: dict[str, str] = {}
for sector in SECTORS:
    for code in sector["krx_industry_codes"]:
        INDUSTRY_TO_SECTOR[code] = sector["id"]


# 주요 종목 수동 매핑 (KRX 업종코드보다 정확한 테마 분류)
MANUAL_MAPPING: dict[str, str] = {
    # 반도체
    "005930": "semiconductor",   # 삼성전자
    "000660": "semiconductor",   # SK하이닉스
    "042700": "semiconductor",   # 한미반도체
    "091990": "bio",             # 셀트리온헬스케어 (바이오가 맞음)
    "005290": "semiconductor",   # 동진쎄미켐
    "336260": "power_energy",    # 두산퓨얼셀 (연료전지 → 전력에너지)
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
