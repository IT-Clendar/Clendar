from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model import recommend_for_user  # model/__init__.py 통해 직접 import 가능


app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# 📄 프론트 페이지 라우팅
@app.route("/")
def home():
    return render_template("1.login.html")

@app.route("/loading")
def loading():
    return render_template("2-1.login-loading.html")

@app.route("/success")
def success():
    return render_template("2-2.login-success.html")

@app.route("/main")
def main():
    return render_template("4.main.html")

@app.route("/profile")
def profile():
    return render_template("3.profile.html")

@app.route("/recommendation-loading")
def recommendation_loading():
    return render_template("6.recommendation-loading.html")

@app.route("/recommendation")
def recommendation():
    return render_template("5.recommendation.html")

# 📡 추천 API (프론트에서 fetch로 호출)
@app.route("/api/recommend")
def api_recommend():
    user_id = request.args.get("user_id", default="1")
    result = recommend_for_user(user_id)
    return jsonify({"recommendations": result})

if __name__ == "__main__":
    app.run(debug=True)