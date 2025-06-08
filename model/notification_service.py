import datetime
from dateutil import parser
from model.calendar_service import fetch_upcoming_events
from model.weather_service import get_weather_data
from model.activity_model import load_model_components, check_suitability, suggest_alternative
from firebase_admin import messaging

# 모델 컴포넌트 로드 (1회만)
model, encoder = load_model_components()

# 좌표 매핑
location_map = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대전': (36.3504, 127.3845),
    '광주': (35.1595, 126.8526),
    '대구': (35.8722, 128.6025)
}

def send_direct_notification(title, body, token):
    """
    FCM을 통해 단일 사용자에게 푸시 알림 전송
    """
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )
    response = messaging.send(message)
    print(f"✅ FCM 알림 전송 완료: {response}")

def run_push_notifications(user_token):
    """
    캘린더에서 일정 조회 → 날씨/모델로 필터 → 푸시 알림 전송
    (현재 시간 기준 1~2시간 이내의 일정만 대상)
    """
    try:
        events = fetch_upcoming_events()
        now = datetime.datetime.utcnow()
        print(f"🔍 현재 시간: {now.isoformat()}")

        for event in events:
            summary = event.get('summary', '제목 없음')
            location_name = event.get('location', '서울').split()[0]
            start_time_str = event.get('start')

            if not start_time_str:
                continue

            try:
                start_time = parser.parse(start_time_str)
                time_diff_sec = (start_time - now).total_seconds()
            except Exception:
                continue

            if 3600 <= time_diff_sec <= 7200:  # 1~2시간 전 알림 대상
                lat, lon = location_map.get(location_name, (37.5665, 126.9780))
                weather = get_weather_data(lat, lon)

                if not weather:
                    continue

                is_suitable = check_suitability(summary, weather, start_time.hour, model, encoder)

                if is_suitable:
                    msg = f"[{summary}] 활동이 곧 시작돼요! ({location_name}, {start_time.strftime('%H:%M')})"
                    send_direct_notification("⏰ 일정 추천 알림", msg, user_token)

    except Exception as e:
        print("❌ 푸시 알림 처리 중 오류:", e)