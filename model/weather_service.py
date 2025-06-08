import os
import requests
from dotenv import load_dotenv


load_dotenv()

# .env 파일에서 API 키 불러오기
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather_data(lat: float, lon: float, lang: str = "kr"):
    if not API_KEY:
        raise ValueError("❌ API 키가 없습니다. .env 파일을 확인하세요.")

    weather_url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang={lang}"
    )
    air_url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={API_KEY}"
    )

    try:
        weather_res = requests.get(weather_url)
        weather_res.raise_for_status()
        weather_data = weather_res.json()

        air_res = requests.get(air_url)
        air_res.raise_for_status()
        air_data = air_res.json()

        result = {
            'temp': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'is_rain': 'rain' in weather_data,
            'pm10': air_data['list'][0]['components']['pm10'],
            'pm25': air_data['list'][0]['components']['pm2_5']
        }

        return result

    except requests.exceptions.RequestException as e:
        print("❗ 날씨 API 요청 오류:", e)
        return None