import os
import json
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)


# ---------- FRONT DOOR (to test the tunnel in a browser) ----------
@app.route("/")
def home():
    return "💅 Diamond's office is open!"


# ---------- THE HANDSHAKE (Slide 3): Meta knocks with a GET ----------
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified by Meta!")
        return challenge, 200          # repeat the code back

    print("❌ Verification failed: wrong token")
    return "Forbidden", 403


# ---------- THE ENVELOPES (Slide 4): Meta delivers with a POST ----------
@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json(silent=True)
    if data is None:
        return "ok", 200               # Rule 1: always reply 200

    # Show the whole envelope (great for learning)
    print("\n📦 New envelope from WhatsApp:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Unpack the boxes carefully (Rule 2)
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # 📩 Customer messages
            for message in value.get("messages", []):
                sender = message.get("from")
                if message.get("type") == "text":
                    text = message["text"]["body"]
                    print(f"📩 Message from {sender}: {text}")
                else:
                    print(f"📩 A {message.get('type')} message from {sender} (not text)")

            # 📬 Updates about messages WE sent
            for status in value.get("statuses", []):
                print(f"📬 Status update: {status.get('status')}")
                for error in status.get("errors", []):
                    print(f"   ❗ Error {error.get('code')}: {error.get('title')}")
                    details = error.get("error_data", {}).get("details")
                    if details:
                        print(f"   📝 Details: {details}")

    return "ok", 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)