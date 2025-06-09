import os, json, tempfile, datetime, traceback
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from firebase_admin import credentials, messaging, initialize_app
from model.weather_service import get_weather_data
from model.calendar_service import fetch_upcoming_events
from model.activity_model import check_suitability, suggest_alternative, load_model_components
from model.notification_service import run_push_notifications
from dateutil import parser
import pytz
from datetime import timezone

# 환경 변수에서 Firebase 결정 정보 가져오기
firebase_json = os.environ.get("FIREBASE_CREDENTIALS")
if not firebase_json:
    raise ValueError("\u274c FIREBASE_CREDENTIALS 환경변수를 체크하세요.")

with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp:
    tmp.write(firebase_json)
    tmp.flush()
    cred = credentials.Certificate(tmp.name)

initialize_app(cred)


# 프로머너 설정
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

model, encoder = load_model_components()

location_map = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대전': (36.3504, 127.3845),
    '광주': (35.1595, 126.8526),
    '대구': (35.8722, 128.6025)
}

USER_DEVICE_TOKEN = "YOUR_CLIENT_DEVICE_TOKEN_HERE"

def send_direct_notification(title, body, token):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )
    response = messaging.send(message)
    print(f"\u2705 알림 전송 완료: {response}")

# ---------------------- HTML 레널리드 ----------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("1.login.html", {"request": request})

@app.get("/loading", response_class=HTMLResponse)
def loading(request: Request):
    return templates.TemplateResponse("2-1.login-loading.html", {"request": request})

@app.get("/success", response_class=HTMLResponse)
def success(request: Request):
    return templates.TemplateResponse("2-2.login-success.html", {"request": request})

@app.get("/main", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse("4.main.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    return templates.TemplateResponse("3.profile.html", {"request": request})

@app.get("/recommendation-loading", response_class=HTMLResponse)
def recommendation_loading(request: Request):
    return templates.TemplateResponse("6.recommendation-loading.html", {"request": request})

@app.get("/recommendation", response_class=HTMLResponse)
def recommendation(request: Request):
    return templates.TemplateResponse("5.recommendation.html", {"request": request})

# ---------------------- API ----------------------
@app.get("/api/recommend")
def api_recommend(user_id: str = "1"):
    try:
        events = fetch_upcoming_events()
        result = []
        now = datetime.datetime.now(datetime.timezone.utc)

        for event in events:
            summary = event.get('summary', '제목 없음')
            location_name = event.get('location', '서울').split()[0]
            start_time_str = event.get('start')

            if not start_time_str:
                continue

            try:
                start_time = parser.parse(start_time_str)
                if start_time.tzinfo is None:
                    start_time=start_time.replace(tzinfo=timezone.utc)
                hour = start_time.hour
            except Exception:
                continue

            lat, lon = location_map.get(location_name, (37.5665, 126.9780))
            weather = get_weather_data(lat, lon)
            if not weather:
                continue

            is_suitable = check_suitability(summary, weather, hour, model, encoder)

            # 한 시간 이내 건 핸드폰 알림 전송
            if 0 <= (start_time - now).total_seconds() <= 3600:
                status = "권장" if is_suitable else "비권장"
                msg = f"[{summary}] 활동이 {status}됩니다. ({location_name}, {start_time_str})"
                send_direct_notification("\ud83d\uddd3 \ud65c동 알림", msg, USER_DEVICE_TOKEN)

            result.append({
                "summary": summary,
                "start": start_time_str,
                "location": location_name,
                "status": "활동 권장" if is_suitable else "비권장",
                "alternative": None if is_suitable else suggest_alternative(summary),
                "weather": weather
            })

        print(f"🎯 최종 추천 결과:{result}")

        return {"recommendations": result}
        

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/trigger-push")
def trigger_push():
    run_push_notifications(USER_DEVICE_TOKEN)
    return "\ud83d\udd14 \ud478시 완료"

# app.py 맨 아래 테스트용으로 추가
if __name__ == "__main__":
    from model.calendar_service import fetch_upcoming_events
    print(fetch_upcoming_events())