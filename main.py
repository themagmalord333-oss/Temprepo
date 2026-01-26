import os
import asyncio
import json
from threading import Thread
from flask import Flask

from pyrogram import Client, filters, enums, idle
from pyrogram.errors import UserNotParticipant, UserAlreadyParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# ✅ SESSION STRING
SESSION_STRING = "BQI5Xz4ATmgtQrG4UVR5E4qQzAhUQ2kcRUfD8eRH_IN1mAQ7oAsp5bO3qNfAJCgU-N9BAt35HMXh-uR-tgYgq8lrTrbTx6edA3l3mD_OigVJ_yTDA6G3Lz30unGo3Bgo7scQzHK6uCXSRabncXw0M5lCkz-mncQLh8ayF0CewrIEc7zNaM7OQEvf9WrKTbru_yQgDx9M_D8qDE-QOeqBiWDYc365i6AIHG-1YFGZNKfEqjgh3gHpQyP6mQb4F_kKXLfULgBZpmqRen--YuKvGPwqv1ZJ_r1DICXKrpxLNGRmjo9HKZyKQ3W4Mz_So47bG1arvdxCllAPvuKYAI2BgQ0_4d-hmgAAAAGc59H6AA"

# 🎯 TARGET SETTINGS
SEARCH_GROUP_ID = -1003227082022
TARGET_INVITE_LINK = "https://t.me/QxentAI"
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
RESOLVED_TARGET_ID = SEARCH_GROUP_ID 

# ==========================================
# 👇 FLASK KEEP-ALIVE SERVER (RENDER FIX)
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


# --- HELPER: CHECK IF USER JOINED ---
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

# --- HELPER: GET JOIN BUTTONS ---
def get_fsub_buttons():
    buttons = []
    for ch in FSUB_CONFIG:
        buttons.append([InlineKeyboardButton(f"📢 Join {ch['username']}", url=ch['link'])])
    
    buttons.append([InlineKeyboardButton("✅ Check Subscription / Try Again", callback_data="check_fsub")])
    return InlineKeyboardMarkup(buttons)

# --- DASHBOARD (UPDATED MENU) ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Bot use karne ke liye neeche diye gaye buttons par click karke channels join karein.",
            reply_markup=get_fsub_buttons()
        )

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
        
        "⚠️ **Note:** Result 30 seconds mein auto-delete ho jayega.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Designed & Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

# --- CALLBACK HANDLER ---
@app.on_callback_query(filters.regex("check_fsub"))
async def check_fsub_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_user_joined(client, user_id):
        await callback_query.message.delete()
        await callback_query.answer("✅ Verified! Welcome back.", show_alert=False)
        await show_dashboard(client, callback_query.message)
    else:
        await callback_query.answer("❌ Abhi bhi join nahi kiya! Pehle Channels Join Karein.", show_alert=True)

# --- MAIN LOGIC (NEW COMMANDS ADDED) ---
COMMAND_LIST = [
    "num", "aadhar", "aadhaar", "email", "vehicle", "vnum", "familyinfo", 
    "gst", "insta", "pak", "cnic", "bomb", "ration", "fastag", "upi2num", "upiinfo"
]

@app.on_message(filters.command(COMMAND_LIST, prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    global RESOLVED_TARGET_ID
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Result dekhne ke liye pehle neeche diye gaye buttons se join karein:",
            reply_markup=get_fsub_buttons()
        )

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via Anysnap...**")

    try:
        # Forward the exact command (e.g., /gst 123) to the target
        sent_req = await client.send_message(RESOLVED_TARGET_ID, message.text)
        target_response = None

        # --- WAIT LOOP ---
        for attempt in range(25): # Increased attempts slightly for heavy tools
            await asyncio.sleep(2.5)
            async for log in client.get_chat_history(RESOLVED_TARGET_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"⏳ **Target Processing... (Attempt {attempt+1})**")
                            break
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **Timeout:** Target bot ne reply nahi diya.")
            return

        # --- Data Extraction ---
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading & Parsing File...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Data Found / Empty Result**")
            return

        # --- JSON Output ---
        json_data = {
            "status": "success",
            "service": "Anysnap Lookup",
            "query_type": message.command[0],
            "input": message.command[1],
            "raw_result": raw_text.strip(),
            "credits": NEW_FOOTER
        }

        final_json_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        formatted_output = f"```json\n{final_json_str}\n```"

        sent_results = []
        if len(formatted_output) > 4000:
            msg1 = await message.reply_text(formatted_output[:4000])
            msg2 = await message.reply_text(formatted_output[4000:])
            sent_results.extend([msg1, msg2])
        else:
            msg = await message.reply_text(formatted_output)
            sent_results.append(msg)

        await status_msg.delete()

        # --- Auto Delete ---
        await asyncio.sleep(30)
        for msg in sent_results:
            try: await msg.delete()
            except: pass

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")


# --- STARTUP FIXER ---
async def start_bot():
    global RESOLVED_TARGET_ID
    print("🚀 Starting Bot...")
    await app.start()
    
    print("🔄 Checking Target Group Access...")
    try:
        try:
            chat = await app.get_chat(SEARCH_GROUP_ID)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Already Member! ID: {RESOLVED_TARGET_ID}")
        except:
            print("⚠️ Not in group. Joining via Link...")
            chat = await app.join_chat(TARGET_INVITE_LINK)
            RESOLVED_TARGET_ID = chat.id
            print(f"✅ Joined Successfully! ID: {RESOLVED_TARGET_ID}")
    except Exception as e:
        print(f"❌ Error Joining/Finding Group: {e}")
        RESOLVED_TARGET_ID = SEARCH_GROUP_ID

    print(f"🚀 Bot is Live! Target Group ID: {RESOLVED_TARGET_ID}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    keep_alive()
    app.run(start_bot())