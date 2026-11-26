# Day 2 exercises
# Exercise 1
print("Exercise 1")

nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

def show_prices(service):
    if service in nail_services:
        return nail_services[service]
    else:
        return "Service not available"

print(show_prices("acrylic"))  # Output: 8000
print(show_prices("manicure"))  # Output: Service not available
print(show_prices("gel polish"))  # Output: 5000


# Exercise 2
print(" Exerecise 2")
def calculate_total(choices):
    total = 0
    for choice in choices:
        if choice in nail_services:
            total += nail_services[choice]
    if total > 15000:
        total *= 0.90  # Apply 10% discount
    return int(total)

print(calculate_total(["acrylic", "gel polish", "french tip"]))  
print(calculate_total(["manicure", "pedicure", "nail art"])) 
print(calculate_total(["acrylic", "french tip"]))  

# Exercise 3
print(" Exercise 3")
# The functions
# The nail_services dictionary

def show_prices():
    print("Here are our services and prices:")
    for service, price in nail_services.items():
        print(f"{service.title()} - ₦{price}")

def get_price(service):
    return nail_services.get(service, "Service not available")

# The Bookings list
bookings = [] 
def make_booking(customer_name):

    service_choice = input("Enter the service you want to book: ").strip().lower()
    if service_choice not in nail_services:
        print(f"Sorry, {service_choice} is not available.")
        return
    
    time = input("What time? ").strip()
    date = input("What date? ").strip()
    price = nail_services[service_choice]
    bookings.append({"customer": customer_name, "service": service_choice, "date": date, "time": time})
    print(f"{customer_name}, your {service_choice.title()} on {date} at {time} is booked. Price: ₦{price}")
    print("Thank you for booking with us!")
    
# The setup
print("Welcome to Nails by Diamond!")
name = input("What is your name? ")

while True:
    command = input(f"\n{name}, type 'prices', 'book', or 'exit': ").strip().lower()
    
    if command == "prices":
        show_prices()
    elif command == "book":
        make_booking(name)
    elif command in nail_services:
        price = get_price(command)
        print(f"{command.title()} costs ₦{price}")
    elif command == "admin":
        print("Admin mode activated.")
        for i, b in enumerate(bookings, start=1):
            print(f"{i}. {b['customer']} - {b['service'].title()} - {b['date']} at {b['time']}")
    elif command == "exit":
        break
    else:
        print("Sorry, I didn't understand that.")
print(f"Bye {name}! You made {len(bookings)} booking(s).")
    
