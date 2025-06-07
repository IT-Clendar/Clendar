import joblib
import os

# model_files 경로에서 모델과 인코더 로드
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../model_files/activity_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "../model_files/activity_label_encoder.pkl")

# 전역 모델 객체 (서버 시작 시 1회만 로딩)
model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

def recommend_for_user(user_id):
    # 📌 여기서 user_id를 기반으로 실제 feature 생성해야 함 (지금은 임시값)
    # 예시 input: [나이, 날씨 민감도, 일정 갯수]
    input_features = [[25, 1, 2]]

    pred = model.predict(input_features)
    labels = encoder.inverse_transform(pred)

    return list(labels)