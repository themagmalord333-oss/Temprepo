import telebot
import json
import os
import subprocess
import threading
import time
from telebot import types
from flask import Flask

# ==========================================
# --- CONFIGURATION ---
# ==========================================
TOKEN = '8321333186:AAEWHHj7OpeS8lARdm1vNjcWOd2ilrc2vWE' 
REQUEST_ID = 5524555108  # Ye wo ID hai jahan request aayegi (Admin)
OWNER_ID = 8081343902    # Aapki ID

# --- PRIVATE CHANNEL ---
MAIN_FORCE_CHANNEL = -1003892920891 
MAIN_FORCE_GROUP = "@Anysnapsupport"
CHANNEL_LINK = "https://t.me/+YOUR_PRIVATE_LINK" # Apna Link Dalein
GROUP_LINK = "https://t.me/Anysnapsupport"

CLONE_COST = 1 # 1 Ref = 1 Clone
# ==========================================

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is Running!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

print("🚀 Main Hosting Bot Starting...")
bot = telebot.TeleBot(TOKEN)
running_bots = {}

if not os.path.exists('clones'): os.makedirs('clones')
USER_DATA_FILE = "users.json"

# --- DATA FUNCTIONS ---
def load_users():
    if not os.path.exists(USER_DATA_FILE): return {}
    try:
        with open(USER_DATA_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_users(data):
    with open(USER_DATA_FILE, 'w') as f: json.dump(data, f)

def get_user_ref_count(user_id):
    data = load_users()
    return data.get(str(user_id), {}).get('referrals', 0)

def set_pending_referral(new_user_id, referrer_id):
    data = load_users()
    new_user_id = str(new_user_id)
    if new_user_id == str(referrer_id): return
    if new_user_id not in data:
        data[new_user_id] = {'referrals': 0, 'invited_by': None, 'pending_ref': str(referrer_id)}
        save_users(data)

def confirm_referral(user_id):
    data = load_users()
    user_id = str(user_id)
    if user_id in data and data[user_id].get('pending_ref'):
        ref_id = data[user_id]['pending_ref']
        if ref_id not in data: data[ref_id] = {'referrals': 0}
        data[ref_id]['referrals'] += 1
        data[user_id]['pending_ref'] = None
        data[user_id]['invited_by'] = ref_id
        save_users(data)
        return ref_id
    return None

def deduct_referrals(user_id, amount):
    data = load_users()
    if data.get(str(user_id), {}).get('referrals', 0) >= amount:
        data[str(user_id)]['referrals'] -= amount
        save_users(data)
        return True
    return False

# --- FORCE JOIN ---
def is_user_joined_main(user_id):
    try:
        s = bot.get_chat_member(MAIN_FORCE_CHANNEL, user_id).status
        return s in ['creator', 'administrator', 'member']
    except: return False

def get_main_join_markup():
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK))
    m.add(types.InlineKeyboardButton("✅ Verify", callback_data="check_main_join"))
    return m

# ==========================================
# 🔥 CLONE BOT TEMPLATE (FIXED)
# ==========================================
def get_clone_code(token, bot_username, custom_credit, subs_list):
    # Dhyan dein: Is code me indentation bilkul left side honi chahiye
    return f"""
import telebot
import time
from telebot import types

TOKEN = "{token}"
REQUEST_ID = {REQUEST_ID}
MY_USERNAME = "{bot_username}"
CUSTOM_CREDIT = "{custom_credit}"

bot = telebot.TeleBot(TOKEN)
request_storage = {{}} # Memory to store chat IDs

# --- 1. START COMMAND (NEW) ---
@bot.message_handler(commands=['start'])
def start_msg(m):
    bot.reply_to(m, f"👋 **Welcome to @{{MY_USERNAME}}!**\\n\\n🆔 Use `/num <number>` to search.\\n\\n📢 Powered By: {{CUSTOM_CREDIT}}", parse_mode="Markdown")

# --- 2. NUM COMMAND (SEND TO ADMIN) ---
@bot.message_handler(commands=['num'])
def handle_num(m):
    try:
        if len(m.text.split()) < 2:
            bot.reply_to(m, "❌ Usage: `/num <mobile>`")
            return
        
        waiting_msg = bot.reply_to(m, "🔍 **Searching... Please Wait!**")
        
        # Admin ko request bhejo
        text_to_admin = f"Request from User: {{m.chat.id}}\\nQuery: {{m.text}}"
        sent_to_admin = bot.send_message(REQUEST_ID, text_to_admin)
        
        # ID save karo taaki reply wapas bhej sakein
        request_storage[sent_to_admin.message_id] = {{'chat_id': m.chat.id, 'wait_id': waiting_msg.message_id}}
    except Exception as e:
        bot.reply_to(m, "❌ Error connecting to server.")

# --- 3. ADMIN REPLY HANDLER (BACK TO USER) ---
@bot.message_handler(content_types=['text', 'photo', 'document'], func=lambda m: m.chat.id == REQUEST_ID and m.reply_to_message)
def admin_reply(m):
    try:
        original_msg_id = m.reply_to_message.message_id
        if original_msg_id in request_storage:
            user_data = request_storage[original_msg_id]
            target_chat = user_data['chat_id']
            wait_msg = user_data['wait_id']
            
            # Searching message delete karo
            try: bot.delete_message(target_chat, wait_msg)
            except: pass
            
            # Admin ka message user ko copy karo
            if m.text:
                final_text = m.text + f"\\n\\n🔥 {{CUSTOM_CREDIT}}"
                bot.send_message(target_chat, final_text)
            else:
                bot.copy_message(target_chat, m.chat.id, m.message_id)
                bot.send_message(target_chat, f"🔥 {{CUSTOM_CREDIT}}")
    except Exception as e:
        print(f"Error: {{e}}")

# Polling loop
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except:
        time.sleep(5)
"""

# ==========================================
# 🎮 MAIN HOSTING BOT COMMANDS
# ==========================================

@bot.message_handler(commands=['start'])
def main_start(m):
    user_id = m.from_user.id
    args = m.text.split()
    if len(args) > 1 and args[1].isdigit():
        set_pending_referral(user_id, args[1])
    
    if not is_user_joined_main(user_id):
        bot.send_message(m.chat.id, "⚠️ **Join Private Channel First!**", reply_markup=get_main_join_markup())
        return
        
    ref_id = confirm_referral(user_id)
    if ref_id:
        try: bot.send_message(ref_id, f"🎉 **Referral +1**\nTotal: {get_user_ref_count(ref_id)}")
        except: pass
        
    show_menu(m)

def show_menu(m):
    refs = get_user_ref_count(m.from_user.id)
    link = f"https://t.me/{bot.get_me().username}?start={m.from_user.id}"
    text = (f"🤖 **Bot Hosting Service**\n\n"
            f"💰 Price: {CLONE_COST} Ref = 1 Clone\n"
            f"👤 Your Refs: {refs}\n"
            f"🔗 Link: `{link}`\n\n"
            f"👇 Type /clone to create bot.")
    bot.reply_to(m, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_main_join")
def verify_join(call):
    if is_user_joined_main(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        confirm_referral(call.from_user.id)
        bot.send_message(call.message.chat.id, "✅ Verified!")
        show_menu(call.message)
    else:
        bot.answer_callback_query(call.id, "❌ Not Joined!", show_alert=True)

@bot.message_handler(commands=['clone'])
def clone_ask(m):
    uid = m.from_user.id
    if not is_user_joined_main(uid):
        bot.send_message(m.chat.id, "⚠️ Join First!", reply_markup=get_main_join_markup())
        return

    if uid != OWNER_ID and get_user_ref_count(uid) < CLONE_COST:
        bot.reply_to(m, f"❌ Low Balance!\nNeed: {CLONE_COST} Refs.")
        return

    msg = bot.reply_to(m, "🔑 **Send Bot Token:**")
    bot.register_next_step_handler(msg, step_token)

def step_token(m):
    try:
        token = m.text.strip()
        u = telebot.TeleBot(token).get_me().username
        msg = bot.reply_to(m, f"✅ Found: @{u}\n\n✍️ **Enter Credit Name:**\n(e.g. By @YourName)")
        bot.register_next_step_handler(msg, step_credit, token, u)
    except:
        bot.reply_to(m, "❌ Invalid Token!")

def step_credit(m, token, uname):
    credit = m.text.strip()
    # Direct creation no force sub needed for clone inside
    create_bot_process(m, token, uname, credit, [])

def create_bot_process(m, token, uname, credit, subs):
    uid = m.from_user.id
    if uid != OWNER_ID:
        if not deduct_referrals(uid, CLONE_COST): return
        
    try:
        user_dir = f"clones/{uid}"
        if not os.path.exists(user_dir): os.makedirs(user_dir)
        
        # Save Python File
        code = get_clone_code(token, uname, credit, subs)
        filepath = f"{user_dir}/{uname}_bot.py"
        with open(filepath, 'w') as f: f.write(code)
        
        # Save Info
        info = {'file': filepath, 'name': uname, 'status': 'pending'}
        with open(f"{user_dir}/{uname}_info.json", 'w') as f: json.dump(info, f)
        
        # Admin Approval
        mk = types.InlineKeyboardMarkup()
        mk.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"ok|{uid}|{uname}"),
               types.InlineKeyboardButton("❌ Reject", callback_data=f"no|{uid}|{uname}"))
        
        bot.reply_to(m, f"⏳ **Request Sent!**\n@{uname}\nWaiting for approval...")
        bot.send_message(OWNER_ID, f"🔔 **New Clone Request**\nUser: {uid}\nBot: @{uname}", reply_markup=mk)
        
    except Exception as e:
        bot.reply_to(m, f"Error: {e}")

# --- APPROVAL SYSTEM ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(('ok|', 'no|')))
def approval(call):
    if call.from_user.id != OWNER_ID: return
    action, uid, name = call.data.split('|')
    path = f"clones/{uid}/{name}_info.json"
    
    if action == 'ok':
        with open(path, 'r') as f: d = json.load(f)
        d['status'] = 'active'
        with open(path, 'w') as f: json.dump(d, f)
        
        # Start Bot
        launch_bot(d['file'], name)
        
        bot.edit_message_text(f"✅ Active: @{name}", call.message.chat.id, call.message.message_id)
        try: bot.send_message(uid, f"✅ **Approved!**\nYour bot @{name} is now running.")
        except: pass
        
    elif action == 'no':
        os.remove(path)
        bot.edit_message_text("❌ Rejected.", call.message.chat.id, call.message.message_id)

def launch_bot(path, name):
    if name in running_bots:
        running_bots[name].terminate()
    running_bots[name] = subprocess.Popen(['python3', path])

def auto_launcher():
    if not os.path.exists('clones'): return
    for uid in os.listdir('clones'):
        p = f"clones/{uid}"
        if os.path.isdir(p):
            for f in os.listdir(p):
                if f.endswith('_info.json'):
                    try:
                        with open(f"{p}/{f}") as j: d = json.load(j)
                        if d['status'] == 'active': launch_bot(d['file'], d['name'])
                    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=auto_launcher, daemon=True).start()
    bot.infinity_polling()
