from .recommender import recommend_for_user
import os
import json
import firebase_admin
from firebase_admin import credentials

if not firebase_admin._apps:
    firebase_json = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_json:
        cred = credentials.Certificate(json.loads(firebase_json))
        firebase_admin.initialize_app(cred)