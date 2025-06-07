import joblib
import os

# model_files 경로에서 모델과 인코더 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../model_files/activity_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "../model_files/activity_label_encoder.pkl")

# 전역 모델 객체 (서버 시작 시 1회만 로딩)
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

def check_suitability(summary, weather, hour, model, encoder):
    # 간단한 더미 로직 예시
    if weather["temp"] < 0 or weather["pm10"] > 80 or weather["description"].find("비") >= 0:
        return False
    return True

def suggest_alternative(summary):
    return f"{summary} 대신 실내 활동 추천!"

def load_model_components():
    return model, encoder