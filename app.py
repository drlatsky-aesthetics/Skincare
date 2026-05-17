import base64
import io
import os
import requests as http_requests
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from agent import SkincareAgent
from export_docx import generate_plan_docx

load_dotenv()

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


@app.route("/publish-page", methods=["POST"])
def publish_page():
    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    gh_owner = os.environ.get("GH_OWNER", "drlatsky-aesthetics")
    gh_repo  = os.environ.get("GH_REPO",  "treasury-patients")
    gh_domain = os.environ.get("GH_DOMAIN", "")

    if not gh_token:
        return jsonify({"error": "GitHub token not configured on server — add GH_TOKEN to Railway variables."}), 500

    data         = request.get_json(silent=True) or {}
    html         = data.get("html", "")
    filename     = data.get("filename", "patient.html")
    patient_name = data.get("patientName", "Patient")

    if not html:
        return jsonify({"error": "No HTML content provided"}), 400

    api_url = f"https://api.github.com/repos/{gh_owner}/{gh_repo}/contents/{filename}"
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
    }

    sha = None
    r = http_requests.get(api_url, headers=headers, timeout=10)
    if r.ok:
        sha = r.json().get("sha")

    content_b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    body = {
        "message": f"{'Update' if sha else 'Add'} patient page: {patient_name}",
        "content": content_b64,
    }
    if sha:
        body["sha"] = sha

    r = http_requests.put(api_url, headers=headers, json=body, timeout=15)
    if not r.ok:
        msg = r.json().get("message", f"GitHub API error {r.status_code}")
        return jsonify({"error": msg}), 500

    if gh_domain:
        url = f"https://{gh_domain}/{filename}"
    else:
        url = f"https://{gh_owner}.github.io/{gh_repo}/{filename}"

    return jsonify({"url": url})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
