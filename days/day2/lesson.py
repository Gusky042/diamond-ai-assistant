price = 8000

if price > 7000:
    print("Premium service")
elif price > 5000:
    print("Standard service")
else:
    print("Budget service")

nail_services = {
    "Gel polish": 5000,
    "Acrylic": 8000,    
    "French tip": 6000,
    "Pedicure": 7000,
    "Nail art": 10000,
}
service = "Acrylic"
is_open = True

if service in nail_services and is_open:
    print("We can do that today!")

#name = input("What is your name? ")
#print(f"Welcome, {name}!")

#age = input("Your age? ")      # user types 20 → "20" (text)
#age = int(age)                 # convert to the number 20

for i in range(3):
    print(f"Reminder {i + 1}: Book your appointment!")

##   message = input("You: ")
   # if message == "exit":
  #      print("Goodbye!")
    #    break                  # break = stop the loop
    #print(f"You said: {message}")

def greet(name):
    return f"Hello {name}, welcome to Nails by Diamond!"

message = greet("Diamond")
print(message)

print(greet("Ada"))


def day_of_week(day="Sunday"):
    return f"today is {day}"

print(day_of_week("Thursday"))
print(day_of_week())

try:
    quantity = int(input("How many? "))
    print(f"You want {quantity}")
except ValueError:
    print("Please enter a number.")