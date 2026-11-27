import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, request
from dotenv import load_dotenv

# =====================================================================
# 1. SETTINGS (secrets from .env)
# =====================================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
GEMINI_HEADERS = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}

WA_VERSION = "v25.0"
WA_URL = f"https://graph.facebook.com/{WA_VERSION}/{PHONE_NUMBER_ID}/messages"
WA_HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

# =====================================================================
# 2. BUSINESS DATA (single source of truth)
# =====================================================================
nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

BOOKINGS_FILE = Path(__file__).parent / "bookings.json"


def load_bookings():
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("⚠️ bookings.json is damaged. Starting with an empty list.")
        return []


def save_bookings():
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(bookings, file, indent=2, ensure_ascii=False)


bookings = load_bookings()

# =====================================================================
# 3. TOOLS (Diamond's hands, from Day 6)
# =====================================================================
def get_price(service):
    service = service.strip().lower()
    if service not in nail_services:
        return {"found": False, "message": f"We don't offer {service}."}
    return {"found": True, "service": service, "price": nail_services[service]}


def make_booking(customer_name, service, booking_date, booking_time, phone=None):
    service = service.strip().lower()

    if service not in nail_services:
        return {"success": False, "message": f"We don't offer {service}."}

    if "sunday" in booking_date.lower():
        return {"success": False, "message": "We are closed on Sundays. Please choose another day."}

    for booking in bookings:
        same_date = booking["date"].strip().lower() == booking_date.strip().lower()
        same_time = booking["time"].strip().lower() == booking_time.strip().lower()
        if same_date and same_time:
            return {"success": False, "message": "That time is already taken. Please choose another time."}

    bookings.append({
        "customer": customer_name,
        "phone": phone,                      # added by OUR code, not the AI (Slide 5)
        "service": service,
        "date": booking_date,
        "time": booking_time,
    })
    save_bookings()

    return {
        "success": True,
        "booking_number": len(bookings),
        "service": service,
        "date": booking_date,
        "time": booking_time,
        "price": nail_services[service],
    }


available_functions = {
    "get_price": get_price,
    "make_booking": make_booking,
}

tools = [
    {
        "functionDeclarations": [
            {
                "name": "get_price",
                "description": "Look up the official price of ONE nail service. Always use this before telling a customer any price.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "The service name, e.g. acrylic or pedicure"}
                    },
                    "required": ["service"],
                },
            },
            {
                "name": "make_booking",
                "description": "Save a booking. Only use this after the customer has given their name, the service, the exact date and the time, AND has confirmed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "The customer's name"},
                        "service": {"type": "string", "description": "The nail service"},
                        "booking_date": {"type": "string", "description": "The exact date in this format: Weekday, DD Month YYYY (e.g. Monday, 07 December 2026)"},
                        "booking_time": {"type": "string", "description": "The time, e.g. 11am or 3pm"},
                    },
                    "required": ["customer_name", "service", "booking_date", "booking_time"],
                },
            },
        ]
    }
]

# =====================================================================
# 4. THE BRIEFING (rebuilt every time, so the date is always correct)
# =====================================================================
def build_system_prompt():
    today = datetime.now().strftime("%A, %d %B %Y")
    service_names = ", ".join(name.title() for name in nail_services)
    return f"""
You are Diamond, the friendly WhatsApp receptionist for Nails by Diamond,
a nail business at ESUT Agbani, Enugu, Nigeria. Today is {today}.

Services we offer: {service_names}.
Opening hours: Monday to Saturday, 9am to 7pm. Closed on Sundays.

Rules:
- To tell a customer any price, ALWAYS use the get_price tool. Never guess a price.
- To book, you need the customer's name, the service, the exact date and the time.
  Ask for anything missing. Never book outside opening hours.
- Once you have the name, service, date and time, send ONE message that repeats all
  the details and asks "Shall I confirm this booking?". Only call make_booking after
  the customer says yes to THAT message. An earlier "yes" does not count.
- If asked about a service we don't offer, politely say we don't offer it and suggest
  our available services. Don't promise to check with the owner about new services.
- Only say a booking is confirmed if make_booking returns success: true.
- When confirming, state the exact date (for example: Saturday, 28 November).
- Reply in the same language as the customer's latest message (English or Pidgin).
- Keep replies short: 1 to 3 sentences. Use *single stars* for bold. Never use ** or #.
- If you are not sure about something, say you will check with the owner.
"""

# =====================================================================
# 5. THE BRAIN (Gemini + the tool dance, from Day 6)
# =====================================================================
def call_gemini(history):
    body = {
        "systemInstruction": {"parts": [{"text": build_system_prompt()}]},
        "contents": history,
        "tools": tools,
    }
    wait = 2
    for attempt in range(1, 5):
        try:
            response = requests.post(GEMINI_URL, headers=GEMINI_HEADERS, json=body, timeout=(10, 90))
        except requests.exceptions.RequestException:
            print("   ⚠️ Network problem (Gemini)...")
        else:
            if response.status_code == 200:
                candidate = response.json().get("candidates", [{}])[0]
                content = candidate.get("content")
                if content is None:
                    print(f"   ⚠️ Gemini gave no content (finishReason: {candidate.get('finishReason')})")
                    return None
                return content
            if response.status_code not in (429, 500, 503):
                print(f"   ❌ Gemini error {response.status_code}: {response.text}")
                return None
            print(f"   ⚠️ Gemini busy ({response.status_code})...")
        if attempt < 4:
            time.sleep(wait)
            wait = wait * 2
    return None


def get_reply(history, customer_phone):
    for step in range(5):                                   # safety limit
        content = call_gemini(history)
        if content is None:
            return None

        history.append(content)                             # save her turn exactly as it came

        function_calls = []
        for part in content.get("parts", []):
            if "functionCall" in part:
                function_calls.append(part["functionCall"])

        if not function_calls:                              # normal text reply, so we're done
            text = ""
            for part in content.get("parts", []):
                text += part.get("text", "")
            return text

        answer_parts = []
        for call in function_calls:
            name = call["name"]
            args = dict(call.get("args", {}))               # a copy we can safely change

            if name == "make_booking":
                args["phone"] = customer_phone              # trusted data from WhatsApp (Slide 5)

            print(f"   🔧 Diamond is using {name} with {args}")

            func = available_functions.get(name)
            if func is None:
                result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = func(**args)
                except TypeError:
                    result = {"error": "Wrong details were given to this tool."}

            function_response = {"name": name, "response": result}
            if "id" in call:
                function_response["id"] = call["id"]
            answer_parts.append({"functionResponse": function_response})

        history.append({"role": "user", "parts": answer_parts})

    return "Sorry, I got confused. Please say that again. 🙏"

# =====================================================================
# 6. MEMORY: one file per customer (Slides 2 and 6)
# =====================================================================
conversations = {}          # phone number → that customer's history
MAX_HISTORY = 30


def is_user_text(entry):
    if entry.get("role") != "user":
        return False
    for part in entry.get("parts", []):
        if "text" in part:
            return True
    return False


def trim_history(history):
    while len(history) > MAX_HISTORY:
        history.pop(0)                                      # tear out the oldest page
    while history and not is_user_text(history[0]):
        history.pop(0)                                      # make sure it starts with a customer message

# =====================================================================
# 7. THE MOUTH (from Day 8)
# =====================================================================
def send_whatsapp(to, text):
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    try:
        response = requests.post(WA_URL, headers=WA_HEADERS, json=body, timeout=(10, 30))
    except requests.exceptions.RequestException:
        print("   ❌ Network problem (WhatsApp).")
        return False

    if response.status_code == 200:
        return True

    error = response.json().get("error", {})
    print(f"   ❌ WhatsApp error {response.status_code} (code {error.get('code')}): {error.get('message')}")
    return False

# =====================================================================
# 8. HANDLING ONE MESSAGE (runs in the background "assistant" thread)
# =====================================================================
processed_ids = set()               # the "DONE" stamps (Slide 3)
brain_lock = threading.Lock()       # one at a time in the filing room (Slide 4)


def handle_message(sender, text):
    with brain_lock:
        # Testing shortcut: "reset" clears this customer's memory
        if text.strip().lower() == "reset":
            conversations[sender] = []
            send_whatsapp(sender, "🔄 Memory cleared. Let's start again!")
            print(f"   🔄 Memory cleared for {sender}")
            return

        history = conversations.setdefault(sender, [])     # get (or create) this customer's file
        start = len(history)
        history.append({"role": "user", "parts": [{"text": text}]})

        reply = get_reply(history, sender)

        if reply is None:                                   # the brain failed
            while len(history) > start:
                history.pop()                               # tear out this turn's pages
            send_whatsapp(sender, "Sorry, I'm having network wahala. Please try again in a moment. 🙏")
            return

        trim_history(history)
        print(f"   💅 Diamond: {reply}")
        send_whatsapp(sender, reply)

# =====================================================================
# 9. THE EARS (webhook, from Day 10)
# =====================================================================
app = Flask(__name__)


@app.route("/")
def home():
    return "💅 Diamond is awake!"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified by Meta!")
        return challenge, 200
    print("❌ Verification failed: wrong token")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def receive():
    data = request.get_json(silent=True)
    if data is None:
        return "ok", 200

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            # 📩 Customer messages
            for message in value.get("messages", []):
                msg_id = message.get("id")
                if msg_id in processed_ids:
                    print("   ↩️ Duplicate envelope, skipping")
                    continue
                processed_ids.add(msg_id)

                sender = message.get("from")
                if message.get("type") == "text":
                    text = message["text"]["body"]
                    print(f"\n📩 {sender}: {text}")
                    threading.Thread(target=handle_message, args=(sender, text)).start()
                else:
                    print(f"\n📩 {sender} sent a {message.get('type')} (not text)")
                    threading.Thread(
                        target=send_whatsapp,
                        args=(sender, "Sorry, I can only read text messages for now. 🙏"),
                    ).start()

            # 📬 Delivery reports
            for status in value.get("statuses", []):
                print(f"   📬 {status.get('status')}")
                for error in status.get("errors", []):
                    print(f"   ❗ Error {error.get('code')}: {error.get('title')}")

    return "ok", 200                                        # sign for the package immediately


if __name__ == "__main__":
    app.run(debug=True, port=5000)