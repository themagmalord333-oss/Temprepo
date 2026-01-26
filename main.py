import os
import asyncio
import json
from threading import Thread
from flask import Flask

from pyrogram import Client, filters, enums, idle
from pyrogram.errors import UserNotParticipant, UserAlreadyParticipant, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# ✅ SESSION STRING
SESSION_STRING = "BQI5Xz4ATmgtQrG4UVR5E4qQzAhUQ2kcRUfD8eRH_IN1mAQ7oAsp5bO3qNfAJCgU-N9BAt35HMXh-uR-tgYgq8lrTrbTx6edA3l3mD_OigVJ_yTDA6G3Lz30unGo3Bgo7scQzHK6uCXSRabncXw0M5lCkz-mncQLh8ayF0CewrIEc7zNaM7OQEvf9WrKTbru_yQgDx9M_D8qDE-QOeqBiWDYc365i6AIHG-1YFGZNKfEqjgh3gHpQyP6mQb4F_kKXLfULgBZpmqRen--YuKvGPwqv1ZJ_r1DICXKrpxLNGRmjo9HKZyKQ3W4Mz_So47bG1arvdxCllAPvuKYAI2BgQ0_4d-hmgAAAAGc59H6AA"

# 🎯 TARGET SETTINGS
TARGET_GROUP_LINK = "QxentAI"
TARGET_BOT_USERNAME = "XshuiBot"

NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# --- 🔐 SECURITY SETTINGS ---
ALLOWED_GROUPS = [-1003387459132]
FSUB_CONFIG = [
    {"username": "Anysnapupdate", "link": "https://t.me/Anysnapupdate"},
    {"username": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- GLOBAL VARIABLE ---
RESOLVED_TARGET_ID = None 

# ==========================================
# 👇 FLASK KEEP-ALIVE
# ==========================================
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Anysnap Bot is Running High!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()
# ==========================================

# --- HELPER FUNCTIONS ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            member = await client.get_chat_member(ch["username"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except Exception:
            pass
    return not missing 

def get_fsub_buttons():
    buttons = []
    for ch in FSUB_CONFIG:
        buttons.append([InlineKeyboardButton(f"📢 Join {ch['username']}", url=ch['link'])])
    buttons.append([InlineKeyboardButton("✅ Check Subscription", callback_data="check_fsub")])
    return InlineKeyboardMarkup(buttons)

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Access Denied! Join Channels first.", reply_markup=get_fsub_buttons())

    text = (
        "📖 **ANYSNAP PREMIUM DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🇮🇳 **INDIAN LOOKUP**\n"
        "📱 Mobile: `/num <number>`\n"
        "🆔 Aadhaar: `/aadhar <number>`\n"
        "🚗 Vehicle: `/vehicle <plate>`\n"
        "👨‍👩‍👧 Family: `/familyinfo <aadhaar>`\n"
        "📧 Email: `/email <email>`\n\n"
        "💼 **FINANCIAL & GOVT**\n"
        "🧾 GST: `/gst <gstin>`\n"
        "💳 Ration: `/ration <number>`\n"
        "🛣️ FASTag: `/fastag <rc_number>`\n"
        "💰 UPI Info: `/upiinfo <vpa>`\n"
        "🔄 FamPay: `/upi2num <fampay_id>`\n\n"
        "🌍 **INTERNATIONAL**\n"
        "🇵🇰 Pak Mobile: `/pak <number>`\n"
        "🆔 Pak CNIC: `/cnic <cnic>`\n\n"
        "🛠️ **TOOLS & SOCIAL**\n"
        "📸 Insta: `/insta <username>`\n"
        "💣 Bomber: `/bomb <number>`\n\n"
        "⚡ **Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("check_fsub"))
async def check_fsub_callback(client, callback_query: CallbackQuery):
    if await check_user_joined(client, callback_query.from_user.id):
        await callback_query.message.delete()
        await show_dashboard(client, callback_query.message)
    else:
        await callback_query.answer("❌ Join channels first!", show_alert=True)

# --- MAIN LOGIC (JSON OUTPUT + CLEANER) ---
COMMAND_LIST = [
    "num", "aadhar", "aadhaar", "email", "vehicle", "vnum", "familyinfo", 
    "gst", "insta", "pak", "cnic", "bomb", "ration", "fastag", "upi2num", "upiinfo"
]

@app.on_message(filters.command(COMMAND_LIST, prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    global RESOLVED_TARGET_ID
    
    if not RESOLVED_TARGET_ID:
        return await message.reply_text("❌ **Error:** Target Group not connected. Contact Admin.")

    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 Access Denied!", reply_markup=get_fsub_buttons())

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via Anysnap...**")

    try:
        sent_req = await client.send_message(chat_id=RESOLVED_TARGET_ID, text=message.text)
        target_response = None

        for attempt in range(25):
            await asyncio.sleep(2)
            async for log in client.get_chat_history(RESOLVED_TARGET_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating"]
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"⏳ **Processing... ({attempt+1})**")
                            break
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **Timeout:** Server is busy.")
            return

        # --- Data Extraction ---
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- 🧹 CLEANING LOGIC (For JSON Cleanliness) ---
        clean_text = raw_text
        trash_list = [
            "════════════════════════════════════",
            "★  CREDIT  ★",
            "@𝐘𝐨𝐮𝐫𝐋𝐨𝐯𝐞𝐎𝐧𝐞𝐬",
            "Join channel",
            "search field", 
            "search value"
        ]
        
        for trash in trash_list:
            clean_text = clean_text.replace(trash, "")
        
        # Format text lines to be clean inside JSON
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        final_clean_text = "\n".join(lines)

        # --- 📝 JSON STRUCTURE ---
        json_data = {
            "status": "success",
            "query": message.command[0],
            "input": message.command[1],
            "result": final_clean_text, # Clean Data inside JSON
            "credits": NEW_FOOTER
        }
        
        formatted_output = f"```json\n{json.dumps(json_data, indent=4, ensure_ascii=False)}\n```"

        if len(formatted_output) > 4000:
            await message.reply_text(formatted_output[:4000])
            await message.reply_text(formatted_output[4000:])
        else:
            await message.reply_text(formatted_output)

        await status_msg.delete()

    except PeerIdInvalid:
        await status_msg.edit("⚠️ **Refreshing... Try again.**")
        await start_bot()
    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

# --- STARTUP FIXER ---
async def start_bot():
    global RESOLVED_TARGET_ID
    print("🚀 Starting Bot...")
    if not app.is_connected:
        await app.start()
    
    print("🔄 Resolving Target...")
    try:
        try:
            chat = await app.join_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Joined! ID: {RESOLVED_TARGET_ID}")
        except UserAlreadyParticipant:
            chat = await app.get_chat(TARGET_GROUP_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Already Member. ID: {RESOLVED_TARGET_ID}")
        except Exception:
            RESOLVED_TARGET_ID = -1003227082022
            
        await app.get_chat(RESOLVED_TARGET_ID)

    except Exception as e:
        print(f"❌ Error: {e}")
        RESOLVED_TARGET_ID = -1003227082022

    print(f"🚀 Ready! Target: {RESOLVED_TARGET_ID}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    keep_alive()
    app.run(start_bot())