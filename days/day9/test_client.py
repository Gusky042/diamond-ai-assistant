import requests

URL = "http://127.0.0.1:5000/echo"

# Test 1: a good envelope
# print("--- Test 1: good message ---")
# response = requests.post(URL, json={"from": "Obi", "text": "How much is acrylic?"}, timeout=10)
# print("Status:", response.status_code)
# print("Diamond replied:", response.json())

# Test 2: an envelope with no text (the guard should catch it)
print("\n--- Test 2: missing text ---")
response = requests.post(URL, json={"from": "Obi"}, timeout=10)
print("Status:", response.status_code)
print("Diamond replied:", response.json())