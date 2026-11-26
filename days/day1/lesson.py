business_name = "Nails by Diamond"
price = 5000
print(business_name)
print(price)

service = "Gel polish"      # str (string) = text, always in quotes
price = 5000                # int (integer) = whole number
rating = 4.8                # float = decimal number
is_open = True              # bool (boolean) = True or False

print(type(service))
print(type(price))
print(type(rating))
print(type(is_open))

name = "Diamond"
age = 20
city = "Lagos"
print(f"My name is {name}, I am {age} years old and I live in {city}.")

services = ["Gel polish", "Acrylic", "French tip", "Pedicure"]

print(services)        # the whole list
print(services[0])     # first item → Gel polish
print(services[2])     # third item → French tip
print(services[-1])    # last item → Pedicure
print(len(services))   # how many items → 4

services.append("Nail art")   # add an item
print(services)

prices = {
    "Gel polish": 5000,
    "Acrylic": 8000,
    "French tip": 6000,

}
print(prices.get("Gel polish"))   # 5000
print(prices["Gel polish"])   # 5000
print(prices.get("Pedicure"))   # None
prices["Pedicure"] = 7000   # add a new key-value pair
print(prices)
#print(prices["Wig"])
print(prices.get("Wig", "Not available"))  # → Not available

for service, price in prices.items():
    print(f"{service} - ₦{price}")

bookings = [
    {"customer": "Ada", "service": "Acrylic", "time": "2pm"},
    {"customer": "Chioma", "service": "Gel polish", "time": "4pm"}
]

print(bookings[0]["customer"])   # → Ada
print(bookings[1]["service"])    # → Gel polish

for booking in bookings:
    print(f"{booking['customer']} booked {booking['service']} at {booking['time']}")

