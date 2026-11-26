import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
from pathlib import Path

# ---------- KEY + ADDRESS ----------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.5-flash-lite"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

# ---------- BUSINESS DATA ----------
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

bookings = load_bookings()        # read the notebook when the program starts

# ---------- 🆕 THE TOOLS (Slide 6) ----------
def get_price(service):
    service = service.strip().lower()
    if service not in nail_services:
        return {"found": False, "message": f"We don't offer {service}."}
    return {"found": True, "service": service, "price": nail_services[service]}


def make_booking(customer_name, service, booking_date, booking_time):
    service = service.strip().lower()

    if service not in nail_services:
        return {
            "success": False,
            "message": f"We don't offer {service}."
        }

    for booking in bookings:
        same_date = booking["date"].strip().lower() == booking_date.strip().lower()
        same_time = booking["time"].strip().lower() == booking_time.strip().lower()
        if same_date and same_time:
            return {
                "success": False,
                "message": "That time is already taken. Please choose another time."
            }

    bookings.append({
        "customer": customer_name,
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

available_functions = {                     # 🆕 the phone contacts (Slide 8)
    "get_price": get_price,
    "make_booking": make_booking,
}

# ---------- 🆕 THE TOOL MENU (Slide 5) ----------
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
                "description": "The exact date in this format: Weekday, DD Month YYYY (e.g. Monday, 07 December 2026).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "The customer's name"},
                        "service": {"type": "string", "description": "The nail service"},
                        "booking_date": {"type": "string", "description": "The exact date, e.g. Saturday, 28 November 2026"},
                        "booking_time": {"type": "string", "description": "The time, e.g. 11am"},
                    },
                    "required": ["customer_name", "service", "booking_date", "booking_time"],
                },
            },
        ]
    }
]

# ---------- 🆕 THE BRIEFING (no prices here any more!) ----------
today = datetime.now().strftime("%A, %d %B %Y")
service_names = ", ".join(name.title() for name in nail_services)

system_prompt = f"""
You are Diamond, the friendly WhatsApp receptionist for Nails by Diamond,
a nail business at ESUT Agbani, Enugu, Nigeria. Today is {today}.

Services we offer: {service_names}.

Rules:
- To tell a customer any price, ALWAYS use the get_price tool. Never guess a price.
- To book, you need the customer's name, the service, the exact date and the time.
- Ask for anything missing. Then use the make_booking tool.
- We're open Monday to Saturday, 9am to 7pm. Closed on Sundays. Never book outside these hours.
- Before calling make_booking, repeat the booking details and ask the customer to confirm. Only book after they say yes
- Only say a booking is confirmed if make_booking returns success: true.
- When confirming, state the exact date (for example: Saturday, 28 November).
- Reply in the same language as the customer's latest message (English or Pidgin).
- Keep replies short: 1 to 3 sentences. Use *single stars* for bold. Never use ** or #.
- If you are not sure about something, say you will check with the owner.
"""

# ---------- CALL THE AI (now returns the whole content, not just text) ----------
def call_gemini(history):
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": history,
        "tools": tools,                                 # 🆕 hand her the tool menu
    }
    wait = 2
    for attempt in range(1, 5):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=(10, 90))
        except requests.exceptions.RequestException:
            print("Network problem...")
        else:
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]  # 🆕 the whole content (text OR slips)
            if response.status_code not in (429, 500, 503):
                print(f"Error {response.status_code}: {response.text}")
                return None
            print(f"Server busy ({response.status_code})...")
        if attempt < 4:
            time.sleep(wait)
            wait = wait * 2
    return None

# ---------- 🆕 THE DANCE (Slides 7–10) ----------
def get_reply(history):
    for step in range(5):                               # safety limit
        content = call_gemini(history)
        if content is None:
            return None

        history.append(content)                         # save her turn exactly as it came

        # 1. Did she send any slips?
        function_calls = []
        for part in content.get("parts", []):
            if "functionCall" in part:
                function_calls.append(part["functionCall"])

        # 2. No slips → it's a normal text reply, so we're done
        if not function_calls:
            text = ""
            for part in content.get("parts", []):
                text += part.get("text", "")
            return text

        # 3. Slips → run each function and collect the answers
        answer_parts = []
        for call in function_calls:
            name = call["name"]
            args = call.get("args", {})
            print(f"   🔧 Diamond is using {name} with {args}")   # so YOU can see it happen

            func = available_functions.get(name)
            if func is None:
                result = {"error": f"Unknown tool: {name}"}
            else:
                try:
                    result = func(**args)               # fill the form and run it
                except TypeError:
                    result = {"error": "Wrong details were given to this tool."}

            function_response = {"name": name, "response": result}
            if "id" in call:
                function_response["id"] = call["id"]    # same reference number
            answer_parts.append({"functionResponse": function_response})

        # 4. Send the answers back, then the loop calls the AI again
        history.append({"role": "user", "parts": answer_parts})

    return "Sorry, I got confused. Please say that again."

# ---------- THE CHAT ----------
history = []
print("💅 Nails by Diamond assistant. Type 'exit' to quit, 'admin' to see bookings.")

while True:
    message = input("You: ").strip()

    if message.lower() == "exit":
        print(f"Bye! 👋 Total bookings: {len(bookings)}")
        break

    if message.lower() == "admin":
        for i, b in enumerate(bookings, start=1):
            print(f"{i}. {b['customer']} - {b['service'].title()} - {b['date']} at {b['time']}")
        continue

    start = len(history)                                # 🆕 remember where this turn began
    history.append({"role": "user", "parts": [{"text": message}]})

    reply = get_reply(history)

    if reply is None:
        while len(history) > start:                     # 🆕 tear out ALL pages from this failed turn
            history.pop()
        print("Diamond: Sorry, network wahala. Please try again.\n")
        continue

    print(f"Diamond: {reply}\n")