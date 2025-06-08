import json

# 로컬에서 firebase 서비스 계정 키 .json 파일 경로
json_path = "firebase_key.json"

# 환경 변수 키 이름
env_key_name = "FIREBASE_CREDENTIALS"

with open(json_path, "r") as f:
    data = json.load(f)

# JSON 문자열로 직렬화 + 이스케이프 처리
env_value = json.dumps(data)

# 최종 .env에 넣을 한 줄 출력
env_line = f'{env_key_name}={env_value}'
print(env_line)