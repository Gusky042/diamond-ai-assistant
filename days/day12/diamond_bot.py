import os
import time
import hmac
import hashlib
import threading
from datetime import datetime

import requests
import psycopg
from psycopg.types.json import Jsonb
from flask import Flask, request
from dotenv import load_dotenv
import functools
print = functools.partial(print, flush=True)

# =====================================================================
# 1. SETTINGS
# =====================================================================
load_dotenv()      # on your laptop: reads .env. On Render: does nothing (settings come from Render)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")          # 🆕 for the wax seal
DATABASE_URL = os.getenv("DATABASE_URL")      # 🆕 the database address

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
GEMINI_HEADERS = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}

WA_VERSION = "v25.0"
WA_URL = f"https://graph.facebook.com/{WA_VERSION}/{PHONE_NUMBER_ID}/messages"
WA_HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}

# =====================================================================
# 2. BUSINESS DATA
# =====================================================================
nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

# =====================================================================
# 3. 🆕 THE DATABASE
# =====================================================================
def db():
    """Open a connection to the database."""
    return psycopg.connect(DATABASE_URL)


def setup_database():
    """Create the 3 tables if they don't exist yet (safe to run every time)."""
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                customer TEXT NOT NULL,
                phone TEXT,
                service TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                phone TEXT PRIMARY KEY,
                history JSONB NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT now()
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_messages (
                id TEXT PRIMARY KEY,
                received_at TIMESTAMPTZ DEFAULT now()
            )
        """)
    print("🗄️ Database ready")


setup_database()

# =====================================================================
# 4. TOOLS (now saving to the database)
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

    with db() as conn:
        # Is this slot already taken? (%s placeholders = safe from SQL injection)
        taken = conn.execute(
            """SELECT 1 FROM bookings
               WHERE lower(trim(booking_date)) = lower(trim(%s))
                 AND lower(trim(booking_time)) = lower(trim(%s))""",
            (booking_date, booking_time),
        ).fetchone()

        if taken:
            return {"success": False, "message": "That time is already taken. Please choose another time."}

        row = conn.execute(
            """INSERT INTO bookings (customer, phone, service, booking_date, booking_time)
               VALUES (%s, %s, %s, %s, %s)
               RETURNING id""",
            (customer_name, phone, service, booking_date, booking_time),
        ).fetchone()

    return {
        "success": True,
        "booking_number": row[0],
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
# 5. THE BRIEFING
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
- Only say a booking is confirmed if make_booking returns success: true.
- Never invent or guess the customer's name. If they haven't told you their name
  in this conversation, ask for it before booking.
- Reply in English by default. Only reply in Pidgin if the customer's LATEST message
  is written in Pidgin. Judge only the latest message, not earlier ones.
- When confirming, state the exact date (for example: Saturday, 28 November).
- If asked about a service we don't offer, politely say we don't offer it and suggest
  our available services. Don't promise to check with the owner about new services.
- Reply in the same language as the customer's latest message (English or Pidgin).
- Keep replies short: 1 to 3 sentences. Use *single stars* for bold. Never use ** or #.
- If you are not sure about something, say you will check with the owner.
"""

# =====================================================================
# 6. THE BRAIN
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
    for step in range(5):
        content = call_gemini(history)
        if content is None:
            return None

        history.append(content)

        function_calls = []
        for part in content.get("parts", []):
            if "functionCall" in part:
                function_calls.append(part["functionCall"])

        if not function_calls:
            text = ""
            for part in content.get("parts", []):
                text += part.get("text", "")
            return text

        answer_parts = []
        for call in function_calls:
            name = call["name"]
            args = dict(call.get("args", {}))
            if name == "make_booking":
                args["phone"] = customer_phone          # trusted data from WhatsApp

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
# 7. 🆕 MEMORY IN THE DATABASE (survives restarts)
# =====================================================================
MAX_HISTORY = 30


def load_history(phone):
    with db() as conn:
        row = conn.execute("SELECT history FROM conversations WHERE phone = %s", (phone,)).fetchone()
    if row is None:
        return []                       # a new customer, so an empty file
    return row[0]


def save_history(phone, history):
    with db() as conn:
        conn.execute(
            """INSERT INTO conversations (phone, history, updated_at)
               VALUES (%s, %s, now())
               ON CONFLICT (phone)
               DO UPDATE SET history = EXCLUDED.history, updated_at = now()""",
            (phone, Jsonb(history)),
        )


def clear_history(phone):
    with db() as conn:
        conn.execute("DELETE FROM conversations WHERE phone = %s", (phone,))


def is_user_text(entry):
    if entry.get("role") != "user":
        return False
    for part in entry.get("parts", []):
        if "text" in part:
            return True
    return False


def trim_history(history):
    while len(history) > MAX_HISTORY:
        history.pop(0)
    while history and not is_user_text(history[0]):
        history.pop(0)


def already_processed(msg_id):
    """Stamp the message 'DONE'. Returns True if it was ALREADY stamped (a duplicate)."""
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO processed_messages (id) VALUES (%s) ON CONFLICT DO NOTHING",
            (msg_id,),
        )
        return cursor.rowcount == 0     # 0 rows added = it was already there

# =====================================================================
# 8. THE MOUTH
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
# 9. HANDLING ONE MESSAGE (with a 🆕 safety net)
# =====================================================================
brain_lock = threading.Lock()


def handle_message(sender, text):
    with brain_lock:
        try:
            if text.strip().lower() == "reset":
                clear_history(sender)
                send_whatsapp(sender, "🔄 Memory cleared. Let's start again!")
                print(f"   🔄 Memory cleared for {sender}")
                return

            history = load_history(sender)                      # open the customer's file
            history.append({"role": "user", "parts": [{"text": text}]})

            reply = get_reply(history, sender)

            if reply is None:
                # We simply DON'T save, so this failed turn disappears on its own
                send_whatsapp(sender, "Sorry, I'm having network wahala. Please try again in a moment. 🙏")
                return

            trim_history(history)
            save_history(sender, history)                       # put the file back in the cabinet
            print(f"   💅 Diamond: {reply}")
            send_whatsapp(sender, reply)

        except Exception as error:                              # 🆕 the safety net
            print(f"   💥 Unexpected error: {error}")
            send_whatsapp(sender, "Sorry, something went wrong on our side. Please try again. 🙏")

# =====================================================================
# 10. 🆕 THE WAX SEAL CHECK
# =====================================================================
def signature_is_valid(req):
    if not APP_SECRET:
        print("⚠️ APP_SECRET is not set!")
        return False
    received = req.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode("utf-8"), req.get_data(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(received, expected)

# =====================================================================
# 11. THE EARS
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
    if not signature_is_valid(request):                         # 🆕 check the wax seal FIRST
        print("🚫 Invalid signature: not from Meta. Ignored.")
        return "Invalid signature", 403

    data = request.get_json(silent=True)
    if data is None:
        return "ok", 200

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})

            for message in value.get("messages", []):
                msg_id = message.get("id")
                if already_processed(msg_id):
                    print("   ↩️ Duplicate envelope, skipping")
                    continue

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

            for status in value.get("statuses", []):
                print(f"   📬 {status.get('status')}")
                for error in status.get("errors", []):
                    print(f"   ❗ Error {error.get('code')}: {error.get('title')}")

    return "ok", 200


if __name__ == "__main__":
    app.run(port=5000)                  # 🆕 no debug mode: this is production code now