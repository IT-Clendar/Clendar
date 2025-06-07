import joblib
import os

def load_model_components():
    model = joblib.load(os.path.join('model_files', 'activity_model.pkl'))
    encoder = joblib.load(os.path.join('model_files', 'activity_label_encoder.pkl'))
    return model, encoder

def check_suitability(activity, weather_info, hour, model, encoder):
    # activity가 학습된 것 중 없는 경우, fallback 처리
    encoded_activity = (
        encoder.transform([activity])[0]
        if activity in encoder.classes_
        else encoder.transform(['실내 요가'])[0]
    )
    features = [[
        weather_info['temp'],
        weather_info['pm25'],
        weather_info['humidity'],
        hour,
        encoded_activity
    ]]
    return model.predict(features)[0] == 1

def suggest_alternative(activity):
    if '러닝' in activity or '산책' in activity:
        return '실내 요가 또는 실내 자전거'
    return '실내 독서나 취미 활동'