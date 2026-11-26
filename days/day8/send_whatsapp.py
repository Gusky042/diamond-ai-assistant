import os
import requests
from dotenv import load_dotenv

# ---------- SECRETS ----------
load_dotenv()
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
MY_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")


# ---------- ADDRESS ----------
API_VERSION = "v26.0"      # check Meta's docs for the latest version
url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"

# ---------- ID CARD ----------
headers = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json",
}

# ---------- THE RECIPE ----------
def send_whatsapp(to, text):
    body = {
        "messaging_product": "whatsapp",   # "this is a WhatsApp message"
        "to": to,                          # who receives it
        "type": "text",                    # a normal text message
        "text": {"body": text},            # the actual words
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=(10, 30))
        print("Meta says:", response.text)
    except requests.exceptions.RequestException:
        print("❌ Network problem.")
        return False

    if response.status_code == 200:
        print("✅ Sent!")
        return True

    error = response.json().get("error", {})
    print(f"❌ Error {response.status_code}: {error.get('message')}")
    return False

# ---------- USE IT ----------
caption = ask_ai("Write a short, warm WhatsApp message from Nails by Diamond in Enugu, "
                 "telling customers we now do French tips. Max 2 sentences. Use *single stars* for bold.")
print("AI wrote:", caption)

if caption:
    send_whatsapp(MY_NUMBER, caption)
# send_whatsapp(MY_NUMBER, "Hello from Python! 💅 This is Diamond's first message.")


def send_template(to):
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }
    response = requests.post(url, headers=headers, json=body, timeout=(10, 30))
    print("Meta says:", response.text)

send_template(MY_NUMBER)