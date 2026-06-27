import io
import os
import re
from flask import Flask, render_template, request, jsonify, send_file, abort, Response
from dotenv import load_dotenv
from agent import SkincareAgent
from export_docx import generate_plan_docx

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Persistent patient-page storage. Backed by a Railway Volume mounted at
# RAILWAY_VOLUME_MOUNT_PATH (falls back to a local ./data dir outside Railway,
# e.g. for local dev) so published pages survive redeploys.
PAGES_DIR = os.path.join(os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "./data"), "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

# Slugs become filenames on disk and segments of a public URL — restrict to a
# safe charset so a crafted slug can't escape PAGES_DIR (e.g. "../../etc").
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")

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


@app.route("/export", methods=["POST"])
def export():
    data = request.get_json(silent=True) or {}
    plan = data.get("plan")
    if not plan or not isinstance(plan, dict):
        return jsonify({"error": "No plan provided"}), 400
    try:
        docx_bytes = generate_plan_docx(plan)
        title = plan.get("title", "Treatment Plan").replace(" ", "_")[:60]
        return send_file(
            io.BytesIO(docx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=f"Treasury_Aesthetics_{title}.docx",
        )
    except Exception as e:
        print(f"[export] error: {e}")
        return jsonify({"error": f"Export failed: {e}"}), 500


@app.route("/api/publish-page", methods=["POST"])
def publish_page():
    auth = request.headers.get("Authorization", "")
    expected = os.environ.get("PUBLISH_TOKEN", "")
    if not expected or auth != f"Bearer {expected}":
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    slug = (data.get("slug") or "").strip().lower()
    html = data.get("html")

    if not SLUG_RE.match(slug):
        return jsonify({"error": "Invalid slug — use lowercase letters, numbers, and hyphens only."}), 400
    if not html or not isinstance(html, str):
        return jsonify({"error": "No html provided"}), 400

    path = os.path.join(PAGES_DIR, f"{slug}.html")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    except OSError as e:
        return jsonify({"error": f"Could not write page: {e}"}), 500

    domain = os.environ.get("APP_DOMAIN", request.host)
    return jsonify({"ok": True, "url": f"https://{domain}/{slug}.html"})


@app.route("/<slug>.html")
def serve_page(slug):
    slug = slug.lower()
    if not SLUG_RE.match(slug):
        abort(404)
    path = os.path.join(PAGES_DIR, f"{slug}.html")
    if not os.path.isfile(path):
        abort(404)
    with open(path, "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
