import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.5-flash-lite"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
headers = {
    "x-goog-api-key": api_key,
    "Content-Type": "application/json",
}



def ask_ai(question):
    body = {"contents":[{"parts":[{"text":question}]}]}

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
                    text += part.get("text", "")      # some parts may have no text, so use .get
                return text
            
            if response.status_code not in (429, 500, 503):
                return f"Error {response.status_code}: {response.text}" 

            print(f"Server busy ({response.status_code})...")

        if attempt < 4:
            time.sleep(wait)
            wait = wait * 2
            
    return "The AI is busy. Please try again later."

print("🤖 AI Chat. Type 'exit' to quit.")

while True:
    message = input("Please input your question or exit: ") .strip()

    if message.lower() == "exit":
        print("Bye")
        break

  
    answer = ask_ai(message)
    print(f"AI: {answer}\n")