import os, base64
import gspread
from google.oauth2.service_account import Credentials
from gtts import gTTS
from pydub import AudioSegment

# 1) 구글 서비스 계정 인증
creds_json = base64.b64decode(os.environ['GCP_CREDENTIALS'])
creds = Credentials.from_service_account_info(
    __import__('json').loads(creds_json),
    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
)
gc = gspread.authorize(creds)

# 2) 시트 열기
SPREADSHEET_ID = '12i8_--tyA-WPjLVjzghgNS-6ejZO8URke1bdA4xbYCg' # <-- 이 부분을 당신의 Google Sheet ID로 교체하세요!
sh = gc.open_by_key(SPREADSHEET_ID)
# 시트 이름이 '전화 영어'와 '영어 일기'인지 다시 한번 확인해 주세요.
exprs = sh.worksheet('전화 영어').col_values(1)
diary = sh.worksheet('영어 일기').col_values(1)

# 3) 텍스트 통합
lines = [l.strip() for l in exprs + [''] + diary if l.strip()]

# 4) TTS 생성 및 병합
audio = AudioSegment.empty()
for i, text in enumerate(lines, 1):
    # 텍스트가 너무 길면 gTTS가 오류를 낼 수 있으므로, 적절히 분할하여 처리할 수 있도록 고려하거나
    # 시트의 한 셀에 너무 긴 문장을 넣지 않도록 주의합니다.
    # 영국식 발음 (tld='co.uk')
    tts = gTTS(text=text, lang='en', tld='co.uk') 
    fname = f'temp_{i}.mp3'
    tts.save(fname)
    seg = AudioSegment.from_mp3(fname)
    audio += seg + AudioSegment.silent(duration=500) # 각 문장 사이에 0.5초 침묵 추가
    os.remove(fname)

# 5) 결과물 저장
out = 'all_phrases.mp3'
audio.export(out, format='mp3')
print(f'{out} 생성 완료')
