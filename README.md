# 💅 Diamond: AI Receptionist for a Nail Business (WhatsApp version coming soon)
An AI assistant for **Nails by Diamond** (ESUT Agbani, Enugu) that chats with customers
in **English and Pidgin**, quotes **real prices**, and **books appointments**, built with
Python and the Google Gemini API.

## ✨ Features
- 💬 Understands natural language: *"Abeg book acrylic for me tomorrow by 3"*
- 🔧 Uses **function calling**: the AI calls Python functions for prices and bookings
- 💰 Prices come only from the business's price list, so they can't be invented
- 📅 Converts "tomorrow" and "Friday" into exact dates
- 🛡️ Blocks double bookings and services the business doesn't offer
- ✅ Confirms with the customer before booking
- 💾 Saves bookings to a JSON file
- 🔁 Retries automatically when the AI server is busy

## 🛠️ Built with
Python · Google Gemini API (REST) · requests · python-dotenv

## 🚀 How to run
1. Clone this repository
2. Install the requirements: `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your Gemini API key
4. Run: `python days/day6/diamond_tools.py`

## 💬 Example conversation
```
You: I want acrylic, my name is Emma
   🔧 Diamond is using get_price with {'service': 'acrylic'}
Diamond: Hello Emma! Acrylic is *8,000 Naira*. What date and time would you like?
You: Friday, by 5pm
Diamond: Emma, I have you down for Acrylic on Friday, 27 November 2026 at 5pm. Shall I confirm?
You: yes
   🔧 Diamond is using make_booking with {'customer_name': 'Chiagozie', 'booking_time': '5pm', 'service': 'Nail Art', 'booking_date': 'Saturday, 28 November 2026'}
Diamond: Your booking is confirmed! 💅
```
## ⚠️ Known limitations
- Runs in the terminal only (WhatsApp integration is next)
- Dates and times are stored as text, so "5pm" and "17:00" aren't recognised as the same time
- Assumes one customer per time slot (one nail technician)
- Bookings are stored in a JSON file, not a database

## 📂 Other projects in this repo
| Project | File | What it shows |
|---|---|---|
| Rule-based nail bot | `days/day2/nails_bot.py` | Python basics, loops, functions |
| Nigerian weather | `days/day3/weather.PY` | Query parameters, live data |
| GitHub profile tool | `days/day4/first_AI_call.py` | Calling APIs, error handling |
| AI chat with memory | `days/day5/diamond_chat.py` | Conversation history, system prompts |

## 🔜 Coming next
- Connecting Diamond to real **WhatsApp**
- A database for bookings

## 📚 What I learned
My journey into Python and AI development has taught me how to move from writing simple lines of code to building applications that can solve real problems. I have learned about functions, APIs, prompts, and how to connect an AI model to Python functions so it can perform tasks instead of just generating text. One of the hardest challenges was understanding how Gemini's function calling works, especially how Python receives a function request, executes it, and sends the result back to Gemini. Fixing and understanding these challenges has improved my confidence and shown me that I don't need to memorise every line of code; I need to understand how the different parts work together.