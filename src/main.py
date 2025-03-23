import re
import spacy
from typing import Dict, List

# 한국어 모델 로드 (spaCy의 경우 기본적으로 한국어 모델이 없음)
# 설치 필요: !pip install spacy & !python -m spacy download ko_core_news_sm
try:
    nlp = spacy.load("ko_core_news_sm")
except:
    nlp = None

def extract_trip_info(text: str) -> Dict[str, str]:
    if not text:
        return {"출장 인원 수": "없음", "출장 인원들": "없음", "출장 기간": "없음", "출장 장소": "없음", "출장 최대 비용": "없음"}

    # 1. 출장 인원들 (더욱 정밀한 문맥 기반 이름 추출 및 후처리)
    person_names = []

    # 패턴 1: [이름] + [직책] (예: 이재영 팀장) - 단어 경계 강화
    title_name_pattern = re.compile(r"\b([가-힣]{2,4})\s*(대리|사장|팀장|매니저|사원|대표|이사)\b") # 단어 경계 \b 추가
    person_names.extend([match.group(1) for match in title_name_pattern.finditer(text)])

    # 패턴 2: [대명사/지칭어구] + [이름] (예: 저와 김민지, 우리 팀에서 이지혜) - 단어 경계 및 패턴 조정
    pronoun_name_pattern = re.compile(r"\b(?:저|나|우리|저희)\s*(?:(?:팀|부서|그룹)\s*에서)?\s*([가-힣]{2,4})\b") # 단어 경계 \b 추가, 패턴 단순화
    person_names.extend([match.group(1) for match in pronoun_name_pattern.finditer(text)])

    # 패턴 3: 쉼표, '그리고', '및' 등으로 연결된 이름 (예: 김소희, 이재영, 홍길동) - 패턴 조정 및 단어 경계 약화 (이름 중간에 쉼표 있을 수 있음)
    comma_name_pattern = re.compile(r"([가-힣]{2,4})(?:,\s*|,\s*그리고\s*|,\s*및\s*)?([가-힣]{2,4})?(?:,\s*|,\s*그리고\s*|,\s*및\s*)?([가-힣]{2,4})?") # 패턴 유지 (단어 경계 제거)
    comma_matches = comma_name_pattern.finditer(text)
    for match in comma_matches:
        for group_index in range(1, 4): # 그룹 1, 2, 3 (최대 3명)
            name = match.group(group_index)
            if name:
                person_names.append(name)


    person_names = [name.strip() for name in person_names if len(name.strip()) >= 2] # 이름 공백 제거, 1글자 이름 제외
    person_names = list(set(person_names))  # 1차 중복 제거

    # --- 후처리 (이름이 아닌 단어 필터링) ---
    stop_words_names = ["출장", "예산", "만원", "정도", "최대", "이번", "해외", "계획", "입니다", "갈려고해", "갈", "예정", "희망", "목적지는", "출장지는", "출장예정", "부서", "팀", "멤버", "인원", "기간", "장소", "비용", "금액", "멤버"] # 불용어 목록 (추가 및 수정 필요)
    location_keywords_filter = ["베트남", "일본", "중국", "미국", "프랑스", "독일", "영국", "도쿄", "뉴욕", "파리", "베이징", "오사카", "나트랑"] # 장소 키워드 (필터링용)
    stop_words_names.extend(location_keywords_filter) # 장소 키워드도 불용어 목록에 추가

    filtered_person_names = []
    for name in person_names:
        if name not in stop_words_names: # 불용어 목록에 없으면 이름으로 간주
            filtered_person_names.append(name)

    person_names = filtered_person_names # 필터링된 이름 목록으로 업데이트
    person_names = list(set(person_names)) # 최종 중복 제거 (2차)


    # 2. 출장 인원 수 (기존 코드와 동일)
    num_people = len(person_names)

    # 3. 출장 기간 (기존 코드와 동일)
    date_pattern = re.compile(r"(\d{1,2}[./월]\s*\d{1,2}[일]?)\s*(-|부터|~)\s*(\d{1,2}[./월]?\s*\d{1,2}[일]?)")
    date_match = date_pattern.search(text)
    if date_match:
        start_date = date_match.group(1).replace("월", ".").replace("일", "").replace(" ", "").zfill(5)
        end_date = date_match.group(3).replace("월", ".").replace("일", "").replace(" ", "").zfill(5)
        trip_period = f"2025{start_date.replace('.', '')}-2025{end_date.replace('.', '')}"
    else:
        trip_period = "없음"

    # 4. 출장 장소 (기존 코드와 동일)
    location_pattern = re.compile(r"(베트남|일본|중국|미국|프랑스|독일|영국|도쿄|뉴욕|파리|베이징|오사카|나트랑)")
    locations = location_pattern.findall(text)
    trip_location = ", ".join(set(locations)) if locations else "없음"

    # 5. 출장 최대 비용 (기존 코드와 동일)
    cost_pattern = re.compile(r"(\d{3,4})[만]?원")
    trip_cost = cost_pattern.findall(text)
    trip_cost = f"{trip_cost[0]}0000원" if trip_cost else "없음"

    return {
        "출장 인원 수": f"{num_people}명" if num_people > 0 else "없음",
        "출장 인원들": ", ".join(person_names) if person_names else "없음",
        "출장 기간": trip_period,
        "출장 장소": trip_location,
        "출장 최대 비용": trip_cost
    }


# 테스트 데이터 (기존과 동일)
test_inputs = [
    "마케팅부서의 김소희 대리, 이재영 대리, 홍길동 사장이 11.01-11.03 베트남 나트랑으로 출장예정이야. 예산은 최대 500만원이야.",
    "IT부서의 최명재 팀장, 신예준 팀장이 2월1일-2월5일 일본 도쿄로 출장을 갈려고해. 예산은 최대 500만원이야.",
    "저와 김민지, 박철수 매니저 함께 12월 25일부터 12월 28일까지 프랑스 파리 출장 계획 중입니다. 비용은 300만원 이내로 부탁드려요.",
    "우리 팀에서 이지혜, 강동우, 그리고 박서준 24년 5월 10일 - 5월 15일 미국 뉴욕 출장 갑니다. 최대 금액은 700만 원.",
    "출장 인원: 2명, 기간: 7월 3일~7월 7일, 장소: 중국 베이징, 예산: 400만원",
    "2024년 10월 20일 - 10월 25일, 출장지는 도쿄, 같이 가는 사람은 나, 김철수, 최대 600만 원",
    "출장 멤버는 김영희, 이민호, 출장 기간은 3월 15일부터 3월 20일, 목적지는 일본 오사카 희망, 예산은 550만원 정도",
    "해외 출장 계획 있습니다. 11월 1일부터 11월 5일까지, 장소는 프랑스 파리, 예산 450만 원",
    "이번 출장은 9월 10일 - 9월 12일, 출장 장소는 뉴욕 입니다.", # 비용 정보 없음
    ""
]

# 실행 및 출력 (기존과 동일)
for i, input_text in enumerate(test_inputs, 1):
    result = extract_trip_info(input_text)
    print(f"[테스트 {i}]")
    print(f"입력: {input_text}")
    print(f"결과: {result}\n")