import requests
url = "https://jsonplaceholder.typicode.com/users"
response = requests.get(url)

if response.status_code == 200:
    users = response.json()
    search_name = input("Enter your name: ").lower()
    found = False
    for i, user in enumerate(users, start=1):
        if search_name in user["name"].lower():
            print(i, "Name:", user["name"])
            print(   "Email:", user["email"])
            print(   "City:", user["address"]["city"])
            print ("\n")
            found = True
    if not found:
        print("no matching user found.")
            