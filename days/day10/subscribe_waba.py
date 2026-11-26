import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("WHATSAPP_TOKEN")

WABA_ID = 1135684859460405   # from the new app's "Try it out" page

url = f"https://graph.facebook.com/v25.0/{WABA_ID}/subscribed_apps"
headers = {"Authorization": f"Bearer {token}"}

# 1. Subscribe (link the WhatsApp account to your app)
response = requests.post(url, headers=headers, timeout=20)
print("Subscribe:", response.status_code, response.text)

# 2. Check which apps are subscribed
response = requests.get(url, headers=headers, timeout=20)
print("Subscribed apps:", response.status_code, response.text)
