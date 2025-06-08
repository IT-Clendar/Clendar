from datetime import datetime, timezone
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import tempfile
import json

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# def get_calendar_service():
#     token_path = 'model/token.json'
#     creds = None
#     if os.path.exists(token_path):
#         creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file('model/credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open(token_path, 'w') as token:
#             token.write(creds.to_json())
#     return build('calendar', 'v3', credentials=creds)

def get_calendar_service():
    creds = None
    token_path = 'model/token.json'

    # 배포용: 토큰이 있으면 그것만 사용
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        raise RuntimeError("❌ token.json 없음 - 로컬에서 먼저 생성하고 배포하세요.")

    return build('calendar', 'v3', credentials=creds)

def fetch_upcoming_events(max_results=10):
    service = get_calendar_service()

    # ✅ timeMin은 UTC 기준 + Z 형식으로 설정
    now_utc = datetime.now(timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_utc,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    parsed = []
    for event in events:
        summary = event.get('summary', '제목 없음')
        location = event.get('location', '서울')
        start = event['start'].get('dateTime') or event['start'].get('date')
        if not start:
            continue
        end = event['end'].get('dateTime') or event['end'].get('date')

        parsed.append({
            'summary': summary,
            'location': location,
            'start': start,
            'end': end
        })
    return parsed