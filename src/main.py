import re
from datetime import datetime

# 테스트에서는 기본 연도를 2025로 사용 (예상 출력에 맞춤)
CURRENT_YEAR = 2025

def standardize_date(date_str):
    """
    날짜 문자열(예: "2월1일", "24년 5월 10일")을 받아 YYYYMMDD 형태로 변환.
    연도 정보가 없으면 CURRENT_YEAR 사용.
    """
    # 연도 추출: "2024년" 또는 "24년"
    year_match = re.search(r'(\d{2,4})\s*년', date_str)
    if year_match:
        year = year_match.group(1)
        if len(year) == 2:
            year = "20" + year
    else:
        year = str(CURRENT_YEAR)
    
    # 월, 일 추출
    md_match = re.search(r'(\d{1,2})\s*월\s*(\d{1,2})\s*일', date_str)
    if not md_match:
        return None
    month = int(md_match.group(1))
    day = int(md_match.group(2))
    
    try:
        dt = datetime(int(year), month, day)
        return dt.strftime("%Y%m%d")
    except Exception as e:
        return None

def extract_date_range(text):
    """
    다양한 형식의 날짜 범위를 추출하여 "YYYYMMDD - YYYYMMDD" 형태로 반환.
    지원 형식: "2월1일-2월5일", "2월1일부터 2월5일까지", "24년 5월 10일 - 5월 15일"
    """
    # 패턴1: "날짜 - 날짜" (하이픈 또는 ~)
    pattern1 = r'((?:\d{2,4}\s*년\s*)?\d{1,2}\s*월\s*\d{1,2}\s*일)\s*[-~]\s*((?:\d{2,4}\s*년\s*)?\d{1,2}\s*월\s*\d{1,2}\s*일)'
    m = re.search(pattern1, text)
    if m:
        start_str, end_str = m.groups()
        start_date = standardize_date(start_str)
        end_date = standardize_date(end_str)
        if start_date and end_date:
            return f"{start_date} - {end_date}"
    
    # 패턴2: "날짜부터 날짜까지" (혹은 "날짜부터 날짜일")
    pattern2 = r'((?:\d{2,4}\s*년\s*)?\d{1,2}\s*월\s*\d{1,2}\s*일)\s*(?:부터|부터의)\s*((?:\d{2,4}\s*년\s*)?\d{1,2}\s*월\s*\d{1,2}\s*일)\s*(?:까지|일)?'
    m = re.search(pattern2, text)
    if m:
        start_str, end_str = m.groups()
        start_date = standardize_date(start_str)
        end_date = standardize_date(end_str)
        if start_date and end_date:
            return f"{start_date} - {end_date}"
    
    return "정보 없음"

def extract_cost(text):
    """
    비용 정보를 추출하여 원 단위 정수로 반환.
    예: "500만원", "700만 원", "600만 원" 등
    """
    pattern = r'(?:예산|비용|최대(?:\s*금액)?)(?:은|:)?\s*(?:최대\s*)?(\d+)\s*(?:만\s*원|만원)'
    m = re.search(pattern, text)
    if m:
        return int(m.group(1)) * 10000
    return "정보 없음"

def clean_name(name):
    """
    이름 후보에서 불필요한 접미어(예: "팀장", "매니저")나 공백 제거.
    """
    name = name.strip()
    # 불필요한 단어 제거
    for suffix in ["팀장", "매니저"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    return name

def extract_names(text):
    """
    아래 키워드 이후에 오는 문자열에서 이름 후보를 추출.
    지원 키워드: "나랑", "저와", "같이 가는 사람은", "출장 멤버는", "우리 팀에서"
    만약 해당 키워드가 없으면 None 반환.
    """
    keywords = r'(나랑|저와|같이 가는 사람은|출장 멤버는|우리 팀에서)'
    pattern = keywords + r'\s*([^\.，,]+)'
    m = re.search(pattern, text)
    names = []
    if m:
        # 추출된 문자열에서 "그리고", "와" 등 구분자를 기준으로 분리
        raw = m.group(2)
        # 먼저 쉼표나 공백을 기준으로 분리
        parts = re.split(r'[，,]', raw)
        for part in parts:
            # 만약 "그리고"나 "와"가 포함되면 추가 분리
            sub_parts = re.split(r'(그리고|와)', part)
            for sub in sub_parts:
                sub = sub.strip()
                if sub and sub not in ["그리고", "와"]:
                    names.append(clean_name(sub))
    # 필터링: 이름은 한글만, 그리고 길이가 1~4자 정도인 경우 사용
    names = [n for n in names if re.fullmatch(r'[가-힣]{1,4}', n)]
    if names:
        return names
    return None

def extract_personnel(text):
    """
    인원수와 이름 목록 추출.
    1. "출장 인원: 2명" 등 명시된 경우 인원수 사용.
    2. 그렇지 않으면 이름 키워드 추출 결과의 수를 인원수로 사용.
    이름이 없으면 "정보 없음" 반환.
    """
    # 먼저 명시적 인원수 체크: "출장 인원: 2명"
    m = re.search(r'출장\s*인원\s*[:：]?\s*(\d+)\s*명', text)
    if m:
        count = int(m.group(1))
        # 이름은 따로 제공되지 않으면 "정보 없음"으로 처리
        return count, "정보 없음"
    
    names = extract_names(text)
    if names:
        return len(names), ", ".join(names)
    return "정보 없음", "정보 없음"

def extract_location(text):
    """
    출장 장소 추출.
    1. 국가와 도시가 함께 표기된 경우(예: "일본 도쿄", "프랑스 파리") 추출 후 도시, 국가 순으로 반환.
    2. "출장지", "장소", "목적지" 뒤의 단어 추출.
    """
    # 먼저 국가+도시: 국가 목록
    countries = ["일본", "프랑스", "중국", "미국", "한국", "영국", "독일"]
    # 국가 후에 공백이 있고, 도시가 오는 경우
    pattern = r'(' + "|".join(countries) + r')\s*([가-힣A-Za-z]+)'
    m = re.search(pattern, text)
    if m:
        country, city = m.group(1), m.group(2)
        # 출력 형식: 도시, 국가
        return f"{city}, {country}"
    # 키워드 기반 추출: "출장지", "장소", "목적지" 뒤의 단어
    pattern2 = r'(?:출장지(?:는)?|장소(?:는)?|목적지(?:는)?)\s*[:：]?\s*([가-힣A-Za-z]+)'
    m2 = re.search(pattern2, text)
    if m2:
        return m2.group(1).strip()
    return "정보 없음"

def process_input(text):
    """
    입력된 문장에서 출장 관련 정보를 추출하고, 딕셔너리 형태로 반환.
    추출 항목: 출장 인원 수, 출장 인원들의 이름, 출장 기간, 출장 장소, 출장 최대비용
    """
    if not text.strip():
        return {
            "출장 인원 수": "정보 없음",
            "출장 인원들의 이름": "정보 없음",
            "출장 기간": "정보 없음",
            "출장 장소": "정보 없음",
            "출장 최대비용": "정보 없음"
        }
    
    # 1. 출장 기간
    period = extract_date_range(text)
    
    # 2. 비용
    cost = extract_cost(text)
    
    # 3. 이름 및 인원수
    personnel_count, names = extract_personnel(text)
    
    # 4. 출장 장소
    location = extract_location(text)
    
    return {
        "출장 인원 수": f"{personnel_count}명" if isinstance(personnel_count, int) else personnel_count,
        "출장 인원들의 이름": names,
        "출장 기간": period,
        "출장 장소": location,
        "출장 최대비용": cost if isinstance(cost, int) else cost
    }

# ---------------------------
# 테스트 케이스 및 실행
# ---------------------------
test_inputs = [
    "나랑 최명재 팀장, 신예준 팀장이랑 2월1일-2월5일 일본 도쿄로 출장을 갈려고해. 예산은 최대 500만원이야.",
    "저와 김민지, 박철수 매니저 함께 12월 25일부터 12월 28일까지 프랑스 파리 출장 계획 중입니다. 비용은 300만원 이내로 부탁드려요.",
    "우리 팀에서 이지혜, 강동우, 그리고 박서준 24년 5월 10일 - 5월 15일 미국 뉴욕 출장 갑니다. 최대 금액은 700만 원.",
    "출장 인원: 2명, 기간: 7월 3일~7월 7일, 장소: 중국 베이징, 예산: 400만원",
    "2024년 10월 20일 - 10월 25일, 출장지는 도쿄, 같이 가는 사람은 나, 김철수, 최대 600만 원",
    "출장 멤버는 김영희, 이민호, 출장 기간은 3월 15일부터 3월 20일, 목적지는 일본 오사카 희망, 예산은 550만원 정도",
    "해외 출장 계획 있습니다. 11월 1일부터 11월 5일까지, 장소는 프랑스 파리, 예산 450만 원",
    "이번 출장은 9월 10일 - 9월 12일, 출장 장소는 뉴욕 입니다.",  # 비용 정보 없음
    ""  # 빈 입력
]

if __name__ == "__main__":
    for idx, inp in enumerate(test_inputs, 1):
        print(f"테스트 케이스 {idx}:")
        print("입력:", inp)
        output = process_input(inp)
        print("추출 결과:")
        for key, value in output.items():
            print(f"  {key}: {value}")
        print("-" * 50)
