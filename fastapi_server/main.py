
# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# from calendar_service import fetch_upcoming_events
# from weather_service import get_weather_data
# from activity_model import check_suitability, suggest_alternative, load_model_components
# from dateutil import parser
# import traceback

# app = FastAPI()
# model, encoder = load_model_components()

# location_map = {
#     '서울': (37.5665, 126.9780),
#     '부산': (35.1796, 129.0756),
#     '대전': (36.3504, 127.3845),
#     '광주': (35.1595, 126.8526),
#     '대구': (35.8722, 128.6025)
# }

# @app.get("/recommendations")
# def get_recommendations():
#     try:
#         events = fetch_upcoming_events()
#         result = []

#         for event in events:
#             summary = event.get('summary', '제목 없음')
#             location_name = event.get('location', '서울').split()[0] if event.get('location') else '서울'
#             start_time = event.get('start')

#             # None 처리 방어 코드
#             if not start_time:
#                 result.append({
#                     "summary": summary,
#                     "start": None,
#                     "location": location_name,
#                     "status": "시작 시간 없음"
#                 })
#                 continue

#             try:
#                 hour = parser.parse(start_time).hour
#             except Exception:
#                 result.append({
#                     "summary": summary,
#                     "start": start_time,
#                     "location": location_name,
#                     "status": "시간 파싱 오류"
#                 })
#                 continue

#             lat, lon = location_map.get(location_name, (37.5665, 126.9780))
#             weather = get_weather_data(lat, lon)

#             if not weather:
#                 result.append({
#                     "summary": summary,
#                     "start": start_time,
#                     "location": location_name,
#                     "status": "날씨 정보 없음"
#                 })
#                 continue

#             if check_suitability(summary, weather, hour, model, encoder):
#                 result.append({
#                     "summary": summary,
#                     "start": start_time,
#                     "location": location_name,
#                     "status": "활동 권장",
#                     "weather": weather
#                 })
#             else:
#                 alt = suggest_alternative(summary)
#                 result.append({
#                     "summary": summary,
#                     "start": start_time,
#                     "location": location_name,
#                     "status": "비권장",
#                     "alternative": alt,
#                     "weather": weather
#                 })

#         return result

#     except Exception as e:
#         traceback.print_exc()
#         return JSONResponse(status_code=500, content={"error": str(e)})

import firebase_admin
from firebase_admin import credentials, messaging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from calendar_service import fetch_upcoming_events
from weather_service import get_weather_data
from activity_model import check_suitability, suggest_alternative, load_model_components
from dateutil import parser
import datetime
import traceback

# Firebase Admin 초기화
# cred = credentials.Certificate("firebase_key.json")
# firebase_admin.initialize_app(cred)
import json
import os
from firebase_admin import credentials, initialize_app

firebase_json = os.environ.get("FIREBASE_CREDENTIALS")
cred = credentials.Certificate(json.loads(firebase_json))
initialize_app(cred)

# 사용자의 디바이스 토큰 (이걸 실제 사용자별로 저장하고 관리해야 함)
USER_DEVICE_TOKEN = "YOUR_CLIENT_DEVICE_TOKEN_HERE"  # <- 이걸 클라이언트 앱에서 받아서 저장해야 함

app = FastAPI()
model, encoder = load_model_components()

location_map = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대전': (36.3504, 127.3845),
    '광주': (35.1595, 126.8526),
    '대구': (35.8722, 128.6025)
}

def send_direct_notification(title, body, token):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )
    response = messaging.send(message)
    print(f"✅ 알림 전송 완료: {response}")

@app.get("/recommendations")
def get_recommendations():
    try:
        events = fetch_upcoming_events()
        result = []
        now = datetime.datetime.utcnow()

        for event in events:
            summary = event.get('summary', '제목 없음')
            location_name = event.get('location', '서울').split()[0]
            start_time_str = event.get('start')

            if not start_time_str:
                continue

            try:
                start_time = parser.parse(start_time_str)
                hour = start_time.hour
            except Exception:
                continue

            lat, lon = location_map.get(location_name, (37.5665, 126.9780))
            weather = get_weather_data(lat, lon)
            if not weather:
                continue

            is_suitable = check_suitability(summary, weather, hour, model, encoder)

            if 0 <= (start_time - now).total_seconds() <= 3600:
                status = "권장" if is_suitable else "비권장"
                msg = f"[{summary}] 활동이 {status}됩니다. ({location_name}, {start_time_str})"
                send_direct_notification("🗓 활동 알림", msg, USER_DEVICE_TOKEN)

            result.append({
                "summary": summary,
                "start": start_time_str,
                "location": location_name,
                "status": "활동 권장" if is_suitable else "비권장",
                "alternative": None if is_suitable else suggest_alternative(summary),
                "weather": weather
            })

        return result

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
