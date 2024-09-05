from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import sqlite3
import random
import string

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '7103679351:AAESbwKLQzqvDedy11n5LmXwDjbmb6WnQzw'

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = user.id
    username = user.username

    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    if c.fetchone() is None:
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        c.execute('INSERT INTO users (user_id, username, referral_code) VALUES (?, ?, ?)', (user_id, username, referral_code))
        conn.commit()

    conn.close()
    update.message.reply_text(f"Welcome {username}! Your referral code is: {referral_code}")

def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    referral_code = context.args[0].upper()

    conn = sqlite3.connect('bot.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE referral_code = ?', (referral_code,))
    referrer = c.fetchone()

    if referrer:
        c.execute('INSERT INTO referrals (referrer_id, referee_id) VALUES (?, ?)', (referrer[0], user_id))
        conn.commit()
        update.message.reply_text("Referral successful!")
    else:
        update.message.reply_text("Invalid referral code.")

    conn.close()

def broadcast(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == 6224931837:  # Replace YOUR_ADMIN_ID with the admin's Telegram ID
        message = ' '.join(context.args)
        conn = sqlite3.connect('bot.db')
        c = conn.cursor()
        
        c.execute('SELECT user_id FROM users')
        users = c.fetchall()

        for user_id in users:
            try:
                context.bot.send_message(chat_id=user_id[0], text=message)
            except Exception as e:
                print(f"Could not send message to {user_id[0]}: {e}")

        conn.close()
        update.message.reply_text("Broadcast sent.")
    else:
        update.message.reply_text("You are not authorized to use this command.")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('refer', refer))
    dispatcher.add_handler(CommandHandler('broadcast', broadcast))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
