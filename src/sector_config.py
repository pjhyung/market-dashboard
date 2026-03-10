# src/sector_config.py

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
        "krx_industry_codes": ["J582", "J581"],
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
        "krx_industry_codes": ["C303", "C302"],
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
        "krx_industry_codes": ["C301", "C302"],
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
        "krx_industry_codes": ["J582", "R901"],
        "keywords": ["게임", "엔터", "콘텐츠", "미디어", "엔터테인먼트"],
    },
    {
        "id": "chemical",
        "name": "화학",
        "color": "#E879F9",
        "etf_ticker": "140710",   # KODEX 화학 (임시)
        "etf_name": "KODEX 화학",
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
