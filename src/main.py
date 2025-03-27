from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 모델과 토크나이저 로드
model_name = "Leo97/KoELECTRA-small-v3-modu-ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# NER 파이프라인 생성
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer)

# 테스트 문장
example_text = "김민수와 정혜진이 서울에서 부산으로 출장 간다. 3월 15일부터 3월 17일까지."

# 개체명 인식 수행
ner_results = ner_pipeline(example_text)

# 출력 확인
for entity in ner_results:
    print(entity)

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

# 개체명 병합 후 출력
merged_results = merge_tokens(ner_results, example_text)
for entity in merged_results:
    print(entity)
