
## Model -> Tokenizer Load 방식
<img width="420" alt="image" src="https://github.com/user-attachments/assets/85c651cd-477a-46f5-8055-9d46d84cc879" />
</br>
https://huggingface.co/Leo97/KoELECTRA-small-v3-modu-ner
    
<br>
<br>

## WordPiece Tokenizer 사용으로 인한 서브워드 토큰화 이슈
- **NER 결과를 구미로 통합** : `B-` 및 `I-`토큰들을 하나의 엔티티로 합쳐서 처리
