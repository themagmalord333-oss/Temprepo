import os
import asyncio
import json
from threading import Thread  # 👈 FLASK THREADING KE LIYE
from flask import Flask       # 👈 FLASK IMPORT

from pyrogram import Client, filters, enums, idle
from pyrogram.errors import UserNotParticipant, UserAlreadyParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# ✅ SESSION STRING
SESSION_STRING = "BQI5Xz4AgSc0H1AqRtF36ztzS0mIwEg3TszfSM4jL-64WvIy5RUvfhviMlQXU7cz3x7jsK7jcnR-_tJ86zSrUXzfuQHXWHjv7vUOEfBZwW1nb-R3ELMKYYoTqlXCiX0q6tf1Aj5PD_ZxCcx3hmi-fkzbxWrSxTI8Z6z5dYDhq85kRE4SgOFtXN9T_85Enn39Wx74BuUIVq2kXlDB_sdPUn89lgmmjLluLjK-pcms2iqAh3n1C5PEdGO7I_qGF5M7ioJxnpidMi0w60a8Bord_TxCcQffU7R_tQ2eALIOM1vtajUQyN7YVDzX_f21jA6BzZkhe-lYEudfhnTieoZ0pbrFYUFbnwAAAAFJSgVkAA"

# 🎯 TARGET SETTINGS
SEARCH_GROUP_ID = -1003426835879  
TARGET_INVITE_LINK = "https://t.me/+CCFcbjG7sIxiOTE1"
TARGET_BOT_USERNAME = "DeepTraceXBot"

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
    # Render assigns PORT via environment variable
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
    # Add buttons from config
    for ch in FSUB_CONFIG:
        buttons.append([InlineKeyboardButton(f"📢 Join {ch['username']}", url=ch['link'])])
    
    # Add Check Button
    buttons.append([InlineKeyboardButton("✅ Check Subscription / Try Again", callback_data="check_fsub")])
    
    return InlineKeyboardMarkup(buttons)

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Bot use karne ke liye neeche diye gaye buttons par click karke channels join karein.",
            reply_markup=get_fsub_buttons()
        )

    text = (
        "📖 **ANYSNAP BOT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📢 **Updates:** [Join Here](https://t.me/Anysnapupdate)\n"
        "👥 **Support:** [Join Here](https://t.me/Anysnapsupport)\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "ᴍᴏʙɪʟᴇ: `/num 98XXXXXX10`\n"
        "ᴀᴀᴅʜᴀᴀʀ: `/aadhaar 1234XXXX9012`\n"
        "ɢsᴛ: `/gst 24ABCDE1234F1Z5`\n"
        "ɪғsᴄ: `/ifsc SBIN0000000`\n"
        "ᴜᴘɪ: `/upi username@bank`\n"
        "ғᴀᴍ: `/fam username@fam`\n"
        "ᴠᴇʜɪᴄʟᴇ: `/vehicle GJ01AB1234`\n"
        "ᴛᴇʟᴇɢʀᴀᴍ: `/tg @username`\n"
        "ᴛʀᴀᴄᴇ: `/trace 98XXXXXXXX`\n"
        "ɢᴍᴀɪʟ: `/gmail example@gmail.com`\n\n"
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

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "aadhaar", "gst", "ifsc", "upi", "fam", "vehicle", "tg", "trace", "gmail"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
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
        sent_req = await client.send_message(RESOLVED_TARGET_ID, message.text)
        target_response = None

        for attempt in range(20):
            await asyncio.sleep(2.5)
            async for log in client.get_chat_history(RESOLVED_TARGET_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"⏳ **DeepTrace Processing... (Attempt {attempt+1})**")
                            break
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.edit("❌ **Timeout:** Target bot ne reply nahi diya.")
            return

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
            await status_msg.edit("❌ **No Data Found**")
            return

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
        chat = await app.join_chat(TARGET_INVITE_LINK)
        RESOLVED_TARGET_ID = chat.id
        print(f"✅ Freshly Joined! Target ID set to: {RESOLVED_TARGET_ID}")
    except UserAlreadyParticipant:
        print("✅ Already in group. Refreshing Cache...")
        found = False
        async for dialog in app.get_dialogs():
            if dialog.chat.id == SEARCH_GROUP_ID:
                RESOLVED_TARGET_ID = dialog.chat.id
                found = True
                print(f"✅ Found Group in Cache! ID: {RESOLVED_TARGET_ID}")
                break
        
        if not found:
            print("⚠️ Cache refresh failed. Attempting force fetch...")
            try:
                chat = await app.get_chat(SEARCH_GROUP_ID)
                RESOLVED_TARGET_ID = chat.id
                print(f"✅ Force Fetched ID: {RESOLVED_TARGET_ID}")
            except Exception as e:
                print(f"❌ CRITICAL: {e}")

    print(f"🚀 Bot is Live! Target Group ID: {RESOLVED_TARGET_ID}")
    await idle()
    await app.stop()

if __name__ == "__main__":
    # 🔥 FLASK SERVER START
    keep_alive()
    # 🚀 BOT START
    app.run(start_bot())