import os
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq

app = Flask(__name__, static_folder=".")
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.post("/api/chat")
def chat():
    if not os.environ.get("GROQ_API_KEY"):
        return jsonify(error="Manca GROQ_API_KEY nelle variabili d'ambiente del server."), 503
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt", "")).strip()
    if not prompt:
        return jsonify(error="Il messaggio è vuoto."), 400
    history = data.get("history", [])
    messages = [{"role":"system","content":"Sei M-AI, un assistente utile e cordiale. Rispondi in italiano se l'utente scrive in italiano. Non inventare fatti e segnala l'incertezza."}]
    if isinstance(history, list):
        for item in history[-20:]:
            if isinstance(item, dict) and item.get("role") in ("user","assistant") and isinstance(item.get("content"), str):
                messages.append({"role":item["role"],"content":item["content"][:8000]})
    messages.append({"role":"user","content":prompt[:8000]})
    try:
        result = client.chat.completions.create(model=os.environ.get("GROQ_MODEL","llama-3.1-8b-instant"), messages=messages)
        return jsonify(answer=result.choices[0].message.content or "")
    except Exception as exc:
        app.logger.exception("Errore chiamata modello")
        return jsonify(error="Il servizio AI non è riuscito a rispondere. Controlla la chiave, il modello e i log del server."), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT","5000")), debug=False)
