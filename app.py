import os
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from agent import SkincareAgent

load_dotenv()

# Debug: print which env vars Railway has injected (names only, not values)
print("[env] available vars:", [k for k in os.environ if "KEY" in k or "TOKEN" in k or "SECRET" in k or "API" in k])
print("[env] ANTHROPIC_API_KEY set:", bool(os.environ.get("ANTHROPIC_API_KEY")))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

try:
    agent = SkincareAgent()
except Exception as e:
    print(f"[startup] Agent init failed: {e}")
    agent = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    # Return an empty 204 so the browser stops logging a 404
    return "", 204


@app.route("/chat", methods=["POST"])
def chat():
    if agent is None:
        return jsonify({"error": "Agent failed to initialise — check server logs."}), 503

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    clean_history = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content")
    ]

    try:
        reply = agent.chat(user_message, clean_history)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[chat] error: {e}")
        return jsonify({"error": f"Something went wrong: {e}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
