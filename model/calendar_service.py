from datetime import datetime
from pytz import timezone
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def fetch_upcoming_events(max_results=10):
    service = get_calendar_service()
    kst= timezone('Asia/Seoul')
    now=datetime.now(kst).isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now + 'Z',
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    parsed = []
    for event in events:
        summary = event.get('summary', '제목 없음')
        location = event.get('location', '서울')
        start = event['start'].get('dateTime') or event['start'].get('date')  # 중요 포인트!
        if not start:
            continue  # 시작 시간 없으면 건너뜀
        end = event['end'].get('dateTime') or event['end'].get('date')

        parsed.append({
            'summary': summary,
            'location': location,
            'start': start,
            'end': end
        })
    return parsed