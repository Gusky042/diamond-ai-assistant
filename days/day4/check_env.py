# import os
# from dotenv import load_dotenv, find_dotenv, dotenv_values

# path = find_dotenv()
# print("1. .env found at:", repr(path))

# if path:
#     print("2. Names inside .env:", list(dotenv_values(path).keys()))
#     load_dotenv(path)
#     print("3. Key loaded:", os.getenv("GEMINI_API_KEY") is not None)

from datetime import datetime

today = datetime.now().strftime("%A, %d %B %Y")
print(today)        # e.g. Wednesday, 25 November 2026