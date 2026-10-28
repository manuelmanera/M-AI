import os
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:path>")
def pages(path):
    return send_from_directory(ROOT, path)

@app.post("/api/chat")
def chat():
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return jsonify(error="Manca GROQ_API_KEY sul server."), 503
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify(error="Messaggio vuoto."), 400
    messages = [{"role": "system", "content": "Sei M-AI, un assistente utile. Rispondi in italiano quando opportuno e non inventare fatti."}]
    history = data.get("history", [])
    if isinstance(history, list):
        for item in history[-20:]:
            if isinstance(item, dict) and item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
                messages.append({"role": item["role"], "content": item["content"][:8000]})
    messages.append({"role": "user", "content": prompt[:8000]})
    try:
        result = Groq(api_key=key).chat.completions.create(
            model=os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=messages
        )
        return jsonify(answer=result.choices[0].message.content or "")
    except Exception:
        app.logger.exception("Groq request failed")
        return jsonify(error="Errore Groq: controlla chiave API, modello e log del server."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
