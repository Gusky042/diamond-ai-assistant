from flask import Flask, request

# 1. Build the shop
app = Flask(__name__)

# 2. Data
nail_services = {
    "gel polish": 5000,
    "acrylic": 8000,
    "french tip": 6000,
    "pedicure": 7000,
    "nail art": 10000,
}

# 3. Counters (routes)

# Front door
@app.route("/")
def home():
    return "💅 Diamond's office is open!"

# Full price list
@app.route("/prices")
def prices():
    return nail_services

# One service's price
@app.route("/price/<service>")
def price(service):
    service = service.strip().lower()
    if service not in nail_services:
        return {"found": False, "message": f"We don't offer {service}."}, 404
    return {"found": True, "service": service, "price": nail_services[service]}

# Greeting with a query parameter, e.g. /hello?name=Obi
@app.route("/hello")
def hello():
    name = request.args.get("name", "friend")
    return f"Hello {name}, welcome to Nails by Diamond! 💅"

# Envelope counter (POST)
@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True)          # open the envelope

    if data is None or "text" not in data:        # guard: empty or no text
        return {"error": "Please send a message with 'text'."}, 400

    sender = data.get("from", "unknown")
    text = data["text"]
    print(f"📩 New message from {sender}: {text}")

    return {"reply": f"Diamond received: {text}"}

# 4. Open the shop (ALWAYS at the very bottom)
if __name__ == "__main__":
    app.run(debug=True, port=5000)