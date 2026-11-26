import os
import time
import requests
from dotenv import load_dotenv

# ==========================================================
# 1. SECRETS (from .env)
# ==========================================================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
MY_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

# ==========================================================
# 2. GEMINI (the brain) - from Day 4
# ==========================================================
MODEL = "gemini-3.5-flash-lite"
gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
gemini_headers = {
    "x-goog-api-key": GEMINI_API_KEY,
    "Content-Type": "application/json",
}


def ask_ai(question):
    body = {"contents": [{"parts": [{"text": question}]}]}

    wait = 2
    for attempt in range(1, 5):
        try:
            response = requests.post(gemini_url, headers=gemini_headers, json=body, timeout=(10, 90))
        except requests.exceptions.RequestException:
            print("Network problem (Gemini)...")
        else:
            if response.status_code == 200:
                data = response.json()
                parts = data["candidates"][0]["content"]["parts"]
                text = ""
                for part in parts:
                    text += part.get("text", "")
                return text

            if response.status_code not in (429, 500, 503):
                print(f"Gemini error {response.status_code}: {response.text}")
                return None

            print(f"Gemini busy ({response.status_code})...")

        if attempt < 4:
            time.sleep(wait)
            wait = wait * 2

    print("Gemini is busy. Please try again later.")
    return None

# ==========================================================
# 3. WHATSAPP (the mouth) - from Day 8
# ==========================================================
API_VERSION = "v25.0"
whatsapp_url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
whatsapp_headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}


def send_whatsapp(to, text):
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = requests.post(whatsapp_url, headers=whatsapp_headers, json=body, timeout=(10, 30))
    except requests.exceptions.RequestException:
        print("❌ Network problem (WhatsApp).")
        return False

    if response.status_code == 200:
        print("✅ Sent to WhatsApp!")
        return True

    error = response.json().get("error", {})
    print(f"❌ WhatsApp error {response.status_code}: {error.get('message')}")
    return False

# ==========================================================
# 4. THE MAGIC MOMENT ✨: brain writes, mouth sends
# ==========================================================
prompt = (
    "Write a short, warm WhatsApp message from Nails by Diamond in ESUT Agbani, Enugu, "
    "telling customers we now do French tips. Maximum 2 sentences. "
    "Use *single stars* for bold. Never use ** or #."
)

print("🧠 Asking Gemini to write the message...")
message = ask_ai(prompt)

if message:
    print("\n📝 Gemini wrote:")
    print(message)
    print("\n📱 Sending to WhatsApp...")
    send_whatsapp(MY_NUMBER, message)
else:
    print("❌ No message to send (Gemini failed).")