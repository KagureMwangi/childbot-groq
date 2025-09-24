from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load Groq API key securely from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing! Set it in Render dashboard → Environment Variables.")

@app.route("/")
def home():
    return "✅ Groq-powered childbot webhook is running!"

def handle_chat(user_input: str):
    """Send user input to Groq API and return the reply"""
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a friendly teacher for toddlers. "
                    "Always answer in very simple grammar. "
                    "Use short sentences. Avoid big words. "
                    "Explain science in fun and true ways. "
                    "Use emojis to help explain."
                ),
            },
            {"role": "user", "content": user_input},
        ],
        "model": "llama3-70b-8192",
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers=headers,
    )

    print("🔎 Groq response status:", response.status_code)
    print("🔎 Groq response text:", response.text)

    if response.status_code != 200:
        return None, f"Groq API error: {response.text}"

    try:
        groq_data = response.json()
        choices = groq_data.get("choices", [])

        if choices and "message" in choices[0]:
            reply = choices[0]["message"].get("content", "No content.")
        else:
            reply = "No reply from Groq."

        return reply, None
    except Exception as e:
        return None, f"Error parsing Groq response: {e}"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📥 Incoming Lovable payload:", data)

    user_input = data.get("user_input", "")
    if not user_input:
        return jsonify({"error": "No user_input field in request"}), 400

    reply, error = handle_chat(user_input)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"reply": reply})

# Add /chat alias for Lovable
@app.route("/chat", methods=["POST"])
def chat():
    return webhook()

if __name__ == "__main__":
    app.run(debug=True)
