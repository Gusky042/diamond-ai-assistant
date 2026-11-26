nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,    
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

bookings = []

def get_price(service):
    service = service.strip().lower()
    if service not in nail_services:
        return {"found": False, "message": f"We don't offer {service}."}
    return {"found": True, "service": service, "price": nail_services[service]}


def make_booking(customer_name, service, booking_date, booking_time):
    service = service.strip().lower()
    if service not in nail_services:                      # guard clause
        return {"success": False, "message": f"We don't offer {service}."}

    bookings.append({
        "customer": customer_name,
        "service": service,
        "date": booking_date,
        "time": booking_time,
    })
    return {
        "success": True,
        "booking_number": len(bookings),
        "service": service,
        "date": booking_date,
        "time": booking_time,
        "price": nail_services[service],
    }

tools = [
    {
        "functionDeclarations": [
            {
                "name": "get_price",
                "description": "Look up the official price of ONE nail service. Always use this before telling a customer any price.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {"type": "string", "description": "The service name, e.g. acrylic or pedicure"}
                    },
                    "required": ["service"]
                }
            },
            {
                "name": "make_booking",
                "description": "Save a booking. Only use this after the customer has given their name, the service, the exact date and the time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "The customer's name"},
                        "service":       {"type": "string", "description": "The nail service"},
                        "booking_date":  {"type": "string", "description": "The exact date, e.g. Saturday, 28 November 2026"},
                        "booking_time":  {"type": "string", "description": "The time, e.g. 11am"}
                    },
                    "required": ["customer_name", "service", "booking_date", "booking_time"]
                }
            }
        ]
    }
]

print(get_price("Acrylic"))
print(get_price("wig"))
print(make_booking("Obi", "pedicure", "Saturday, 28 November 2026", "11am"))
print(make_booking("Ada", "wig", "Monday", "2pm"))
print(bookings)
