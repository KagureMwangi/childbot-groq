from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set your Groq API key securely (use environment variables in production!)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/")
def home():
    return "Groq-powered webhook is running!"

@app.route("/webhook", methods=["POST"])
def get_recipe():
    try:
        data = request.get_json()
        print("Incoming Lovable payload:", data)

        user_input = data.get("user_input", "")
        if not user_input:
            return jsonify({"error": "No message received"}), 400

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a friendly teacher for toddlers. "
                    "Always answer in very simple grammar. "
                    "Use short sentences. Avoid big words. "
                    "Explain science in fun and true ways. "
                    "Use emojis to help explain."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "model": "llama3-70b-8192",  # or another available Groq model
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)

        # Debug the raw Groq response
        print("Groq response status:", response.status_code)
        print("Groq response JSON:", response.text)

        if response.status_code != 200:
            return jsonify({"error": "Groq API failed", "details": response.text}), 500

        try:
            groq_data = response.json()
            reply = groq_data.get("choices", [{}])[0].get("message", {}).get("content", "Sorry, no content.")
        except Exception as e:
            print("Error parsing Groq response:", e)
            return jsonify({"error": "Invalid response from Groq", "details": response.text}), 500

        return jsonify({"reply": reply})

    except Exception as e:
        print("Unhandled server error:", e)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)