import nltk
import spacy
import konlpy
import gensim
import sklearn
import transformers
import pandas as pd
import numpy as np

print("자연어 처리 개발 환경 구축 완료!")

# 간단한 NLTK 테스트 (영어 토큰화)
text = "This is a sample sentence for NLTK testing."
tokens = nltk.word_tokenize(text)
print("NLTK 토큰화 결과:", tokens)

# 간단한 KoNLPy 테스트 (한국어 형태소 분석)
from konlpy.tag import Okt
okt = Okt()
korean_text = "한국어 자연어 처리 테스트 문장입니다."
morphs = okt.morphs(korean_text)
print("KoNLPy 형태소 분석 결과:", morphs)