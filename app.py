from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os, base64

app = Flask(__name__, static_url_path='', static_folder='.')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    lang = data.get("lang", "auto")

    if not user_message:
        return jsonify({"reply": "Brak wiadomości."}), 400

    # Wykrywanie języka użytkownika
    sys_prompt = "Odpowiadaj w tym samym języku, w jakim użytkownik pisze."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Jesteś przyjaznym i pomocnym asystentem o nazwie KloseCore, stworzonym przez Dawida Klose w 2025 roku. {sys_prompt}"},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route("/voice_reply", methods=["POST"])
def voice_reply():
    data = request.get_json()
    user_message = data.get("message", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś naturalnym asystentem AI KloseCore. Odpowiadasz w tym samym języku, w jakim mówi użytkownik."},
            {"role": "user", "content": user_message}
        ]
    )

    text_reply = response.choices[0].message.content

    try:
        speech = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text_reply
        )
        audio_base64 = base64.b64encode(speech.read()).decode("utf-8")
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
    except Exception:
        audio_url = None

    return jsonify({"reply": text_reply, "audio": audio_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
