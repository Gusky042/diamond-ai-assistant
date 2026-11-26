import os
import time
from dotenv import load_dotenv
import requests 
from datetime import datetime


# print(today)        # e.g. Wednesday, 25 November 2026
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
today = datetime.now().strftime("%A, %d %B %Y")
MODEL = "gemini-3.5-flash-lite"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
headers = {
    "x-goog-api-key": api_key,
    "Content-Type": "application/json",
}

# Business data

nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

price_list = ""

for service, price in nail_services.items():
    price_list += f"- {service.title()}: ₦{price}\n"

system_prompt = f"""
You are Diamond, the friendly WhatsApp receptionist for Nails by Diamond,
a nail business at ESUT Agbani, Enugu, Nigeria.

Our services and prices:
{price_list}
Today is {today}.
Rules:

- Only use the prices above. Never invent prices, discounts or services.
- If asked about a service not on the list, politely say we don't offer it.
- Keep replies short: 1 to 3 sentences.
- Use WhatsApp formatting: *single stars* for bold. Never use ** or #.
- Reply in the same language as the customer's latest message: English if they write English, Pidgin if they write Pidgin.
- If someone wants to book, ask for: the service, the date, and the time.
- When confirming a booking, always state the exact date (for example: Saturday, 28 November). If the customer's date is unclear, ask them to confirm.
- If you are not sure about something, say you will check with the owner.
"""
def ask_ai(history):
    body = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},   
        "contents": history,                                         
    }

    wait = 2

    for attempt in range(1, 5):
        try:
            response = requests.post(url, headers=headers, json=body, timeout=(10,90))
        except requests.exceptions.RequestException:
            print("Network problem...") 
        else:
            if response.status_code == 200:
                data = response.json()
                parts = data["candidates"][0]["content"]["parts"]
                text = ""
                for part in parts:
                    text += part.get("text", "")
                return text

            if response.status_code not in (429, 500, 503):
                print(f"Error {response.status_code}: {response.text}")
                return None

            print(f"Server busy ({response.status_code})...")

        if attempt < 4:
            time.sleep(wait)
            wait = wait * 2

    print("The AI is busy. Please try again later.")
    return None

history = []                                          # the empty file

print("💅 Nails by Diamond assistant. Type 'exit' to quit.")

while True:
    message = input("You: ").strip()

    if message.lower() == "exit":
        print("Bye! 👋")
        break

    history.append({"role": "user", "parts": [{"text": message}]})
    answer = ask_ai(history)

    if history is None:
        answer.pop()
        continue

    history.append({"role": "model", "parts": [{"text": answer}]})

    print(f"Diamond: {answer}\n")
