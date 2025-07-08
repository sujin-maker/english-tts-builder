import os
import gspread
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.silence import detect_silence
import base64 # Base64 모듈은 더 이상 직접 필요하지 않지만, 기존 코드에 있다면 유지해도 무방

# Google Sheets 설정
# TODO: 여기에 실제 Google Sheet ID를 입력하세요.
SPREADSHEET_ID = '12i8_--tyA-WPjLVjzghgNS-6ejZO8URke1bdA4xbYCg' # 제공해주신 시트 ID로 업데이트됨

# Google Sheets API 인증 (이 부분을 아래와 같이 통째로 교체합니다)
# ----------------------------------------------------------------------
gc = gspread.service_account(filename='credentials.json') # 생성된 credentials.json 파일을 사용
# ----------------------------------------------------------------------

sh = gc.open_by_id(SPREADSHEET_ID)

# ... (나머지 코드는 동일) ...

# 각 탭에서 텍스트 읽기
all_phrases = []
# '전화 영어' 탭 읽기
try:
    tele_eng_sheet = sh.worksheet('전화 영어')
    tele_eng_phrases = [cell for cell in tele_eng_sheet.col_values(1) if cell.strip()]
    all_phrases.extend(tele_eng_phrases)
except gspread.exceptions.WorksheetNotFound:
    print("경고: '전화 영어' 시트를 찾을 수 없습니다. 건너뜝니다.")

# '영어 일기' 탭 읽기
try:
    eng_diary_sheet = sh.worksheet('영어 일기')
    eng_diary_phrases = [cell for cell in eng_diary_sheet.col_values(1) if cell.strip()]
    all_phrases.extend(eng_diary_phrases)
except gspread.exceptions.WorksheetNotFound:
    print("경고: '영어 일기' 시트를 찾을 수 없습니다. 건너킵니다.")

# 중복 제거 (필요하다면)
# all_phrases = list(set(all_phrases))

if not all_phrases:
    print("Google Sheet에서 읽을 텍스트가 없습니다. 스크립트를 종료합니다.")
    exit()

# Google Text-to-Speech 클라이언트 설정
client = texttospeech.TextToSpeechClient()

# 오디오 병합 준비
combined_audio = AudioSegment.empty()

for i, text in enumerate(all_phrases):
    if not text.strip():
        continue # 빈 문자열은 건너뜀

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE # 또는 MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    try:
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # 생성된 오디오를 AudioSegment로 변환
        audio_segment = AudioSegment.from_file(io.BytesIO(response.audio_content), format="mp3")
        combined_audio += audio_segment

        # 각 문장 후에 0.5초의 간격 추가 (선택 사항)
        combined_audio += AudioSegment.silent(duration=500) # 500ms = 0.5초

        print(f"'{text}' 텍스트 음성 변환 완료. ({i+1}/{len(all_phrases)})")

    except Exception as e:
        print(f"'{text}' 텍스트 음성 변환 중 오류 발생: {e}")
        continue # 오류 발생 시 다음 텍스트로 진행

# 최종 오디오 파일 저장
output_filename = "all_phrases.mp3"
combined_audio.export(output_filename, format="mp3")
print(f"모든 텍스트가 {output_filename}으로 성공적으로 병합되었습니다.")
