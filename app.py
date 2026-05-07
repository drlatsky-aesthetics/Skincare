import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from agent import SkincareAgent

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

agent = SkincareAgent()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Validate history shape to avoid passing malformed data to the API
    clean_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ]

    reply = agent.chat(user_message, clean_history)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
