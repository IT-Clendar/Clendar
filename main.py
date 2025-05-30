# main.py

from fetch_calendar import fetch_upcoming_events
from fetch_weather import get_weather_data
import datetime

# 위치명 → 위도/경도 매핑
location_map = {
    '서울': (37.5665, 126.9780),
    '부산': (35.1796, 129.0756),
    '대전': (36.3504, 127.3845),
    '광주': (35.1595, 126.8526),
    '대구': (35.8722, 128.6025)
}

# 1. 캘린더 일정 가져오기
events = fetch_upcoming_events(max_results=5)

if not events:
    print("📭 다가오는 일정이 없습니다.")
else:
    print("📆 일정 기반 날씨 추천 결과\n")

# 2. 각 일정에 대해 날씨 확인 및 추천
for event in events:
    summary = event['summary']
    location_name = event['location'].split()[0] if event['location'] else '서울'
    start_time_str = event['start']

    # 날짜/시간 변환
    try:
        start_dt = datetime.datetime.fromisoformat(start_time_str)
        time_str = start_dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        time_str = start_time_str

    # 위치 매핑 → 위도/경도
    lat, lon = location_map.get(location_name, (37.5665, 126.9780))  # 기본: 서울

    # 날씨 정보 호출
    weather = get_weather_data(lat, lon)

    print(f"📅 [{summary}] {time_str} @ {location_name}")

    if not weather:
        print("⚠️ 날씨 정보를 가져오지 못했습니다.\n")
        continue

    # 출력 + 간단 추천
    print(f"🌤 날씨: {weather['description']}, 🌡 {weather['temp']}°C, 💧습도: {weather['humidity']}%")
    print(f"🧪 미세먼지 PM2.5: {weather['pm25']} µg/m³")
    if weather['is_rain'] or weather['pm25'] > 35:
        print("❌ 활동 권장: 실내 활동을 추천드려요.\n")
    elif weather['pm25'] <= 15:
        print("✅ 활동 권장: 매우 좋아요! 야외 활동 적극 추천!\n")
    else:
        print("🟡 활동 권장: 괜찮지만 약간의 주의가 필요해요.\n")