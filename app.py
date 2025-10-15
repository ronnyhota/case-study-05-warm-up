import os, json, subprocess, shlex, pathlib
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.get("/")
def home():
    return "UVA SDS GPT is alive.", 200

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")

@app.post("/api/chat")
def chat():
    try:
        data = request.get_json(force=True)
        prompt = (data.get("prompt") or data.get("text") or "").strip()
    except Exception as e:
        return jsonify({"error": f"JSON parsing failed: {e}"}), 400

    if not prompt:
        return jsonify({"reply": "(empty prompt)"}), 200

    if not os.getenv("USE_OLLAMA", "").lower() in {"1", "true", "yes"}:
        return jsonify({"reply": prompt}), 200

    system_prefix = "You are UVA SDS GPT. Answer concisely.\n"
    full_prompt = system_prefix + prompt

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": full_prompt},
            timeout=60,
        )
        try:
            js = r.json()
            text = js.get("response", "")
        except ValueError:
            text = ""
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    text += json.loads(line).get("response", "")
                except Exception:
                    pass
        return jsonify({"reply": text.strip() or "(no response)"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 502

@app.post("/api/echo")
def echo():
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    return jsonify({"reply": text if text else "?"}), 200

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)