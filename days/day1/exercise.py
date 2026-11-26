# Day 1 Exercises
# Exercise 1
nail_services = {
    "Gel polish": 5000,
    "Acrylic": 8000,    
    "French tip": 6000,
    "Pedicure": 7000,
    "Nail art": 10000,
}
print("Welcome to Nails by Diamond!")
print("Here are our services and prices:")
for serivce, price in nail_services.items():
    print(f"{serivce} - ₦{price}")

# Exercise 2
customer_choices = ["Gel polish", "Pedicure", "Nail art"]
total = 0
for choice in customer_choices:
    if choice in nail_services:
        total += nail_services[choice]
print(f"Total cost: ₦{total}")

# Exercise 3
bookings = [
    {"customer": "Ada", "service": "Acrylic", "time": "2pm"},
    {"customer": "Chioma", "service": "Gel polish", "time": "4pm"},
    {"customer": "Tunde", "service": "Pedicure", "time": "1pm"},
    {"customer": "Emeka", "service": "Wig", "time": "5pm"}
]
for booking in bookings:
    price = nail_services.get(booking["service"], None)
    if price is None:
        price_text = "not available"
    else:
        price_text = f"₦{price}"
    print(f"{booking['customer']} booked {booking['service']}, at {booking['time']}, and the price is {price_text}.")

