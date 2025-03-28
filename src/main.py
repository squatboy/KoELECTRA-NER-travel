import json
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from datetime import datetime

# 모델과 토크나이저 로드
model_name = "Leo97/KoELECTRA-small-v3-modu-ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# NER 파이프라인 생성
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

# 서브워드 토큰화 문제 해결 - 토큰 병합
def merge_tokens(ner_results, text):
    merged_entities = []
    current_entity = None

    for token in ner_results:
        word = token["word"].replace("##", "")  # 서브워드 처리
        entity = token["entity"]
        score = token["score"]
        start, end = token["start"], token["end"]

        if entity.startswith("B-") or current_entity is None:
            if current_entity:
                merged_entities.append(current_entity)
            current_entity = {"entity": entity[2:], "word": word, "score": score, "start": start, "end": end}
        else:
            current_entity["word"] += word
            current_entity["end"] = end
            current_entity["score"] = (current_entity["score"] + score) / 2  # 평균 점수 계산

    if current_entity:
        merged_entities.append(current_entity)

    return merged_entities

# 도메인에 필요한 정보 추출 (인원, 장소, 기간, 비용)
def extract_business_trip_info(ner_results, text):
    """
    NER 결과에서 출장에 필요한 정보(인원, 장소, 기간, 비용)를 추출하는 함수
    """
    people, locations, dates = [], [], []
    
    # 비용 추출: 정규표현식을 사용하여 "최대 예산은 500만원" 패턴 검색
    cost = None
    cost_pattern = r"(?:최대\s*)?(?:예산|비용)(?:은)?\s*(\d+)\s*(만원|원)"
    cost_match = re.search(cost_pattern, text)
    if cost_match:
        number = int(cost_match.group(1))
        unit = cost_match.group(2)
        if unit == "만원":
            cost_value = number * 10000
        else:
            cost_value = number
        cost = f"{cost_value:,}원"  # 천단위 콤마 추가

    # NER 결과를 통한 정보 추출
    for entity in merge_tokens(ner_results, text):  # 서브워드 병합된 결과 사용
        entity_type = entity["entity"]
        entity_value = entity["word"]

        if entity_type == "PS":  # 사람(Person)
            people.append(entity_value)
        elif entity_type == "LC":  # 장소(Location)
            locations.append(entity_value)
        elif entity_type == "DT":  # 날짜(Date)
            dates.append(entity_value)

    # 날짜 처리: 정규표현식을 사용하여 직접 날짜 추출
    if not dates:
        date_pattern = r"(\d{1,2}/\d{1,2})~(\d{1,2}/\d{1,2})"
        date_match = re.search(date_pattern, text)
        if date_match:
            dates.append(date_match.group(1))
            dates.append(date_match.group(2))

    # 시작일과 종료일 분리 (‘~’, ‘부터’, ‘까지’ 모두 고려)
    start_date = None
    end_date = None
    if dates:
        # 날짜 정보가 하나의 문자열에 모두 포함된 경우 (예: "2/15~2/20" 또는 "2월15일부터 2월20일까지")
        date_text = dates[0] if len(dates) == 1 else f"{dates[0]}~{dates[1]}"
        # 우선 "~" 구분자를 확인
        if "~" in date_text:
            parts = date_text.split("~")
            start_date = parts[0].strip()
            end_date = parts[1].strip()
        else:
            # "부터"와 "까지" 기준으로 처리
            if "부터" in date_text:
                start_date = date_text.split("부터")[0].strip()
                if "까지" in date_text:
                    end_date = date_text.split("까지")[0].split("부터")[-1].strip()

        # 날짜 형식 통일: "2/15" -> "2월15일", 이후 YYYYMMDD로 변환
        date_pattern = r"(\d+)/(\d+)"
        start_date = re.sub(date_pattern, r"\1월\2일", start_date) if start_date else None
        end_date = re.sub(date_pattern, r"\1월\2일", end_date) if end_date else None

        # YYYYMMDD 형식으로 변환
        current_year = datetime.now().year
        date_conversion_pattern = r"(\d+)월(\d+)일"
        if start_date:
            start_date = re.sub(date_conversion_pattern, lambda m: f"{current_year}{int(m.group(1)):02d}{int(m.group(2)):02d}", start_date)
        if end_date:
            end_date = re.sub(date_conversion_pattern, lambda m: f"{current_year}{int(m.group(1)):02d}{int(m.group(2)):02d}", end_date)

    # 출장 정보 정리
    trip_info = {
        "출장 인원": people,
        "출장 인원 수" : len(people),
        "출장 장소": {
            "출발지": locations[0] if locations else None,
            "도착지": " ".join(locations[1:]) if len(locations) > 1 else None,
        },
        "출장 기간": {
            "시작일": start_date,
            "종료일": end_date,
        },
        "최대 비용": cost
    }

    return trip_info

# 예제 문장 변경
example_text = "IT부서의 최명재, 신예준, 이재영이 서울에서 일본 도쿄로 출장 예정이야. 출장기간은 2/15~2/20, 최대 비용 1200만원이야."
ner_results = ner_pipeline(example_text)  # NER 실행

# 정보 추출 result
trip_info = extract_business_trip_info(ner_results, example_text)

# JSON 형식으로 보기 좋게 출력
formatted_output = json.dumps(trip_info, indent=4, ensure_ascii=False)
print(formatted_output)

# 개체명 병합 후 출력 (디버깅용)
merged_results = merge_tokens(ner_results, example_text)
for entity in merged_results:
    print(entity)
