from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Replace with your actual bot token
TOKEN = 'YOUR_BOT_TOKEN'

# In-memory storage for simplicity
users = {}  # user_id -> {'referrer': referrer_id, 'referred': [list_of_referred_ids]}
rewards = {}  # user_id -> reward_points

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = (
        "Welcome! You can use the following commands:\n"
        "/refer - Get your referral link\n"
        "/check_reward - Check your rewards\n"
    )
    update.message.reply_text(text)

def refer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    ref_link = f"http://t.me/YourBotUsername?start={user_id}"
    text = f"Your referral link: {ref_link}\nShare this link to invite others!"
    update.message.reply_text(text)

def check_reward(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    reward_points = rewards.get(user_id, 0)
    text = f"You have {reward_points} reward points."
    update.message.reply_text(text)

def handle_start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    args = context.args
    
    if args:
        referrer_id = int(args[0])
        if referrer_id != user_id:
            # Register referral
            if referrer_id in users:
                users[referrer_id]['referred'].append(user_id)
            else:
                users[referrer_id] = {'referrer': None, 'referred': [user_id]}
            
            # Register new user
            users[user_id] = {'referrer': referrer_id, 'referred': []}
            
            # Update rewards
            rewards[referrer_id] = rewards.get(referrer_id, 0) + 10  # Example reward points
            rewards[user_id] = rewards.get(user_id, 0) + 5  # Example reward points for the new user

            update.message.reply_text("You have been successfully referred!")
        else:
            update.message.reply_text("You cannot refer yourself.")
    else:
        update.message.reply_text("Please use the referral link to refer others.")

def main() -> None:
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("refer", refer))
    dp.add_handler(CommandHandler("check_reward", check_reward))
    dp.add_handler(CommandHandler("start", handle_start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
