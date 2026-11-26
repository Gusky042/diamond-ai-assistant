# # Exercise 1

# import requests


# while True:
#     username  = input("Enter a username or exit: ").strip()
#     if username.lower() == "exit":
#         print("Bye")
#         break

#     url = f"https://api.github.com/users/{username}"
    
#     try:
#         response = requests.get(url, timeout=10)
#     except requests.exceptions.RequestException:
#         print("Network problem. Check your internet connection.")
#         continue

#     if response.status_code == 200:
#         data = response.json()
#         name = data.get("name") or "Not provided"
#         location = data.get("location") or "Not provided"
#         print("Name:", name)
#         print("Location:", location)
#         print("Followers:", data["followers"])
#         print("Public repos:", data["public_repos"])
#         print()

#     elif response.status_code == 404:
#         print("user not found")

#     else:
#         print(f"Error {response.status_code}: {response.json().get('message')}")

# Exercise 2
# 1 - Import
# import requests

# # 2 - create city dictionaries

# cities = {
#     "enugu": (6.44, 7.50),
#     "lagos": (6.52, 3.38),
#     "abuja": (9.08, 7.40),
# }

# while True:
#     # 3- Ask a user for a city name
#     city = input("Please enter a name of a City or exit: ").strip().lower()

#     if city.lower() == "exit":
#         print("bye")
#         break

#     elif city in cities:
#         # 4- unpack coordiates
#         latitude, longitude = cities[city]


#         # 5 - Create parameters
#         params = {
#             "latitude": latitude,
#             "longitude": longitude,
#             "current": "temperature_2m,wind_speed_10m", 
#         }

#         # 6 - call the Open-Meteo API
#         url = "https://api.open-meteo.com/v1/forecast"

#         # 7 - check for network before getting the url
#         try:
#             response = requests.get(url, params=params, timeout=10)
#         except requests.exceptions.RequestException:
#             print("Network problem. Check your internet connection.")
#         else:   

#             # 8 - Check for the forecast
#             if response.status_code == 200:
#                 forecast = response.json()
#                 current = forecast["current"]
#                 units = forecast["current_units"]
#                 temp = current["temperature_2m"]
#                 wind = current["wind_speed_10m"]

#                 print(f"Current weather in {city.title()}: {temp}{units['temperature_2m']}, {wind}{units['wind_speed_10m']}")
#             else:
#                 print(f"Error {response.status_code}: {response.text}")
#     else:
#         print("City not found")

# 1 - Import requests
import requests




# 2 - loop
while True:
    # 2a - user enters a username or exit
    username = input("Enter a username or exit: ").strip().lower()

    # 2b - condition that prints the repos
    if username == "exit":
        print("Bye")
        break

    url = f"https://api.github.com/users/{username}/repos"
    

    try:
        response = requests.get(url, params={"per_page": 100}, timeout=10)
    except requests.exceptions.RequestException:
        print("Network problem. Check your internet connection.")
        continue
    else:

        if response.status_code == 200:
            repos = response.json()   
            
            
            if len(repos) == 0:
                print("This user has no public repos.")
                continue
            print(f"{username} has {len(repos)} public repos")
            best = repos[0]
                        
            for repo in repos:
                print(f"{repo['name']} - ⭐ {repo['stargazers_count']}")
                if repo["stargazers_count"] > best["stargazers_count"]:
                    best = repo
                    
            print()
            print("This is the highest starred repo")
            print(f"{best["name"]} - ⭐ {best["stargazers_count"]}")

        elif response.status_code == 404:
            print("user not found")

        else:
            print(f"Error {response.status_code}: {response.json().get('message')}")