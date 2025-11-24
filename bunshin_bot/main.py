import telebot
from config import bunshin_token
import json
import threading
import time
import os

bot = telebot.TeleBot(bunshin_token)

NOTES = "notes.json"

# helper function
def load_notes():
    if not os.path.exists(NOTES):
        return{}
    with open(NOTES, "r") as f:
        return json.load(f)

def save_notes(notes):
    with open(NOTES, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def schedule_reminder(chat_id, text, delay):
    def job():
        try:
            bot.send_message(chat_id, f"Reminder: {text}")
        except Exception as e:
            print(f"Failed to send reminder: {e}")
    timer = threading.Timer(delay, job)
    timer.daemon = True
    timer.start()

# ensure notes file exists
if not os.path.exists(NOTES):
    save_notes({})


# /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    user = message.from_user
    bot.reply_to(message, f"Sup, {user.first_name}! I'm Bunshin Bot. How's it going? \nType /help to see commands.")

# /help
@bot.message_handler(commands=["help"])
def handle_help(message):
    help_text = (
        "Commands:\n"
        "/note add <text> - save a note\n"
        "/note list - list your notes\n"
        "/note clear - clear your notes\n"
        "/remind <seconds> <text> - remind you after N seconds\n"
        "/help - show this help message "
        "or just type anything and I'll echo it back!"
    )
    bot.reply_to(message, help_text)


# /note
@bot.message_handler(commands=["note"])
def handle_note(message):
    parts = message.text.split(maxsplit=2) # split into at most 3 parts
    user_id = str(message.from_user.id)
    notes = load_notes()

    if len(parts) < 2:
        bot.reply_to(message, "Usage: /note add <your-note> | /note list | /note clear")
        return
    
    sub = parts[1].lower()
    if sub == "add":
        if len(parts) < 3:
            bot.reply_to(message, "Please add your note after /note add")
            return
        data = parts[2]
        notes.setdefault(user_id, []).append(data)
        save_notes(notes)
        bot.reply_to(message, "Note Saved!")
    elif sub == "list":
        notes = data.get(user_id, [])
        if not notes:
            bot.reply_to(message, "You have no notes.")
            return
        txt = "Your notes: \n" + "\n".join(f"{i+1}. {n['text']}" for i, n in enumerate(notes))
        bot.reply_to(message, txt)
    elif sub == "clear": 
        notes[user_id] = []
        save_notes(notes)
        bot.reply_to(message, "Notes Cleared!")
    else:
        bot.reply_to(message, "Unknown subcommand. Use add, list, or clear.")


# /remindme
@bot.message_handler(commands=["remindme"])
def handle_remindme(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "Usage: /remindme <seconds> <your-reminder>")
        return
    try:
        seconds = int(parts[1])
        if seconds <= 0:
            raise ValueError("Seconds must be positive")
    except ValueError:
        bot.reply_to(message, "Please provide valid number of seconds.")
        return
    reminder_text = parts[2]
    schedule_reminder(message.chat.id, reminder_text, seconds)
    bot.reply_to(message, f"Got it, I'll remind you in {seconds} seconds.")

# echo handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, f"You said: {message.text}")

if __name__ == "__main__":
    bot.polling()
    print("Bunshin Bot is polling | https://t.me/bunshin_bot | Ctrl+C to stop")