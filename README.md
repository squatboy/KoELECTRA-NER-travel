# `NER` 기반 정보 추출
## `NER` Model Info
- `Tokenizer Load`
<img width="420" alt="image" src="https://github.com/user-attachments/assets/85c651cd-477a-46f5-8055-9d46d84cc879" />
</br>
https://huggingface.co/Leo97/KoELECTRA-small-v3-modu-ner
  
<br>
<br>

---

## WordPiece Tokenizer 사용으로 인한 서브워드 토큰화 이슈
- **NER 결과를 구미로 통합** : `B-` 및 `I-`토큰들을 하나의 엔티티로 합쳐서 처리
```python
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
            current_entity["score"] = (current_entity["score"] + score) / 2
```
<br>

## 정보들의 input 표현 가능성에 대한 각각의 처리 로직 확장
- 비용 표현을 보다 유연하게 인식할 수 있도록 정규표현식을 확장
  
```python
import re

def extract_cost(text):
    cost_pattern = r"(비용은|예산|최대 비용)\s*(\d{1,3}(?:,\d{3})*)\s*(만원|원)?"
    cost_match = re.search(cost_pattern, text)
    if cost_match:
        number_str = cost_match.group(2)
        number = int(number_str.replace(",", ""))  # 쉼표 제거 후 정수 변환
        unit = cost_match.group(3)

        if unit == "만원" or not unit:
            cost_value = number * 10000  # 만원 단위 기본 처리
        else:
            cost_value = number  # 원 단위일 경우 그대로 사용

        return f"{cost_value:,}원"
    return None
```

<br>

- 다양한 날짜 표현을 인식할 수 있도록 ~, 부터, 까지 등의 표현을 고려하여 시작일과 종료일을 구분
```python
# 날짜 처리
def extract_dates(dates):
    start_date, end_date = None, None
    if dates:
        date_text = dates[0]
        if "~" in date_text:
            parts = date_text.split("~")
            start_date, end_date = parts[0].strip(), parts[1].strip()
        elif "부터" in date_text:
            start_date = date_text.split("부터")[0].strip()
            if "까지" in date_text:
                end_date = date_text.split("까지")[0].split("부터")[-1].strip()
    return start_date, end_date
```
