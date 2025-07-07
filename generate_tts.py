import os
import base64
import gspread
from google.oauth2.service_account import Credentials
from gtts import gTTS

# --- 1) GCP 인증 복원 ---
creds_json = base64.b64decode(os.environ["GCP_CREDENTIALS"])
creds = Credentials.from_service_account_info(
    __import__("json").loads(creds_json),
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
)
gc = gspread.authorize(creds)

# --- 2) 스프레드시트 열기 ---
SPREADSHEET_ID = "12i8_--tyA-WPjLVjzghgNS-6ejZO8URke1bdA4xbYCg"
sh = gc.open_by_key(SPREADSHEET_ID)
exprs = sh.worksheet("Expressions").col_values(1)
diary = sh.worksheet("Diary").col_values(1)

# --- 3) 전체 텍스트 합치기 ---
lines = [l.strip() for l in exprs + [""] + diary if l.strip()]
full_text = " . ".join(lines)

# --- 4) 한 번에 TTS 생성 ---
tts = gTTS(text=full_text, lang="en", tld="co.uk")
tts.save("all_phrases.mp3")
print("✅ all_phrases.mp3 생성 완료")
