# import joblib
# import os

# # model_files 경로에서 모델과 인코더 로드
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "../model_files/activity_model.pkl")
# ENCODER_PATH = os.path.join(BASE_DIR, "../model_files/activity_label_encoder.pkl")

# # 전역 모델 객체 (서버 시작 시 1회만 로딩)
# model = joblib.load(MODEL_PATH)
# encoder = joblib.load(ENCODER_PATH)

# def recommend_for_user(user_id):
#     # 📌 여기서 user_id를 기반으로 실제 feature 생성해야 함 (지금은 임시값)
#     # 예시 input: [나이, 날씨 민감도, 일정 갯수]
#     input_features = [[25, 1, 2]]

#     pred = model.predict(input_features)
#     labels = encoder.inverse_transform(pred)

#     return list(labels)

# model/recommender.py
# model/recommender.py

from .calendar_service import fetch_upcoming_events
from .weather_service import get_weather_data
from .activity_model import check_suitability, suggest_alternative, load_model_components
from dateutil import parser
from datetime import datetime, timezone
import traceback

# 모델 로드
model, encoder = load_model_components()

# 기본 지역 좌표
location_map = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대전': (36.3504, 127.3845),
    '광주': (35.1595, 126.8526),
    '대구': (35.8722, 128.6025)
}

def recommend_for_user(user_id="1"):
    try:
        events = fetch_upcoming_events()
        result = []
        now = datetime.now(timezone.utc)

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
        return [{"error": str(e)}]