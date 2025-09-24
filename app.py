from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load Groq API key from environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


@app.route("/")
def home():
    return "Groq-powered webhook is running!"


def handle_chat(user_input):
    """Send the user input to Groq and return reply + error message (if any)."""
    if not GROQ_API_KEY:
        return None, "❌ GROQ_API_KEY is missing in environment!"

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

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )

        print("🔎 Groq response status:", response.status_code)
        print("🔎 Groq response text:", response.text)

        if response.status_code != 200:
            return None, f"Groq API error: {response.text}"

        groq_data = response.json()
        reply = (
            groq_data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        if not reply:
            return None, "Empty reply from Groq"
        return reply, None

    except Exception as e:
        print("❌ Exception while calling Groq:", str(e))
        return None, str(e)


@app.route("/chat", methods=["POST"])
def chat():
    """Main chat webhook endpoint."""
    try:
        data = request.get_json(force=True)
        print("📩 Incoming Lovable payload:", data)

        user_input = data.get("user_input", "")
        if not user_input:
            return jsonify({"error": "No message received"}), 400

        reply, error = handle_chat(user_input)

        if error:
            print("⚠️ Error occurred:", error)
            # Fallback safe reply
            reply = (
                "Hmm 🤔 I don't know that right now. "
                "But the sky is blue because sunlight scatters in the air 🌤️"
            )

        return jsonify({"reply": reply})

    except Exception as e:
        print("💥 Unhandled server error:", str(e))
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)
