# NLTK에서 필요한 데이터 파일인 punkt_tab을 다운받기 위한 script
# SSL 인증서 검증 무시하고 다운로드

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt_tab')