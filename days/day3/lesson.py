import requests

response = requests.get("https://jsonplaceholder.typicode.com/users/1")

# print(response.status_code)
# print(response.json())
# print("headers")
# print(response.headers)
# print("text")
# print(response.text)
# print("content")
# print(response.content)
# print("url")
# print(response.url)
import requests

# url = "https://jsonplaceholder.typicode.com/users/1"

# response = requests.get(url)

# if response.status_code == 200:
#     user = response.json()

#     print("User:", user["name"])
#     print("Email:", user["email"])

# else:
#     print("Something went wrong!")

# url = "https://jsonplaceholder.typicode.com/users"

# response = requests.get(url)
# if response.status_code == 200:
#     users = response.json()
#     search_name = input("Enter your name: ")
#     found = False
#     for user in users:
    
#         if search_name.lower() in user["name"].lower():
#             print("User found:")
#             print("Name:", user["name"])
#             print("Username:", user["username"])
#             print("Email:", user["email"])
#             print("City:", user["address"]["city"])

#             found = True
   
#     if not found:
#         print("User not found.")
# else:
#     print("Something went wrong!")
# url = "https://jsonplaceholder.typicode.com/users"
# response = requests.get(url)

# if response.status_code == 200:
#     users = response.json()
#     search_name = input("Enter your name: ").lower()
#     found = False
#     for i, user in enumerate(users, start=1):
#         if search_name in user["name"].lower():
#             print(i, "Name:", user["name"])
#             print(   "Email:", user["email"])
#             print(   "City:", user["address"]["city"])
#             print ("\n")
#             found = True
#     if not found:
#         print("no matching user found.")
import requests

# response = requests.get("https://api.github.com/users/torvalds")



# url = "https://api.open-meteo.com/v1/forecast"
# params = {
#     "latitude": 6.44,
#     "longitude": 7.50,
#     "current": "temperature_2m,wind_speed_10m"
# }

# response = requests.get(url, params=params)
# data = response.json()

# print(data)

# current = data["current"]            # step 1: open the outer box
# temp = current["temperature_2m"]     # step 2: open the inner box
# print(f"It is {temp}°C in Enugu right now")

# # or in one line, read left to right:
# print(data["current"]["temperature_2m"])

# response = requests.get("https://api.github.com/users/torvalds/repos")
# repos = response.json()

# print(type(repos))      # <class 'list'>
# print(len(repos))       # how many repos came back

# for repo in repos:
#     print(f"{repo['name']} - ⭐ {repo['stargazers_count']}")

# username = "this-user-does-not-exist-12345"
# response = requests.get(f"https://api.github.com/users/{username}")

# if response.status_code == 200:
#     data = response.json()
#     print(data["name"])
# elif response.status_code == 404:
#     print("User not found.")
# else:
#     print(f"Something went wrong. Status: {response.status_code}")

# try:
#     response = requests.get("https://api.github.com/users/torvalds", timeout=10)

