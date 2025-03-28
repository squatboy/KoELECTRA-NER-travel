# output
# {'entity': 'B-PS', 'score': 0.98651475, 'index': 1, 'word': '김민', 'start': 0, 'end': 2}
# {'entity': 'I-PS', 'score': 0.9643779, 'index': 2, 'word': '##수', 'start': 2, 'end': 3}
# {'entity': 'B-PS', 'score': 0.9851303, 'index': 4, 'word': '정혜', 'start': 5, 'end': 7}
# {'entity': 'I-PS', 'score': 0.9753617, 'index': 5, 'word': '##진', 'start': 7, 'end': 8}
# {'entity': 'B-LC', 'score': 0.96146035, 'index': 7, 'word': '서울', 'start': 10, 'end': 12}
# {'entity': 'B-LC', 'score': 0.94671685, 'index': 10, 'word': '부산', 'start': 15, 'end': 17}
# {'entity': 'B-DT', 'score': 0.9254558, 'index': 12, 'word': '3', 'start': 20, 'end': 21}
# {'entity': 'I-DT', 'score': 0.9526009, 'index': 13, 'word': '##월', 'start': 21, 'end': 22}
# {'entity': 'I-DT', 'score': 0.963946, 'index': 14, 'word': '15', 'start': 23, 'end': 25}
# {'entity': 'I-DT', 'score': 0.9655288, 'index': 15, 'word': '##일', 'start': 25, 'end': 26}
# {'entity': 'I-DT', 'score': 0.93977803, 'index': 16, 'word': '##부터', 'start': 26, 'end': 28}
# {'entity': 'I-DT', 'score': 0.86626637, 'index': 17, 'word': '3', 'start': 29, 'end': 30}
# {'entity': 'I-DT', 'score': 0.8294799, 'index': 18, 'word': '##월', 'start': 30, 'end': 31}
# {'entity': 'I-DT', 'score': 0.82268816, 'index': 19, 'word': '17', 'start': 32, 'end': 34}
# {'entity': 'I-DT', 'score': 0.76479125, 'index': 20, 'word': '##일', 'start': 34, 'end': 35}
# {'entity': 'I-DT', 'score': 0.7750262, 'index': 21, 'word': '##까', 'start': 35, 'end': 36}
# {'entity': 'I-DT', 'score': 0.7814053, 'index': 22, 'word': '##지', 'start': 36, 'end': 37}

def extract_business_trip_info(text):
    ner_results = ner(text)

    people = []
    locations = []
    dates = []

    for entity in ner_results:
        if "PS" in entity["entity"]:  # 사람
            people.append(entity["word"])
        elif "LC" in entity["entity"]:  # 장소
            locations.append(entity["word"])
        elif "DT" in entity["entity"]:  # 날짜
            dates.append(entity["word"])

    return {
        "출장 인원": list(set(people)),
        "출장 장소": list(set(locations)),
        "출장 날짜": list(set(dates)),
    }

# 예제 실행
text = "최명재와 이재영이 서울에서 부산으로 3월 15일부터 3월 17일까지 출장을 갑니다."
trip_info = extract_business_trip_info(text)

print(trip_info)
