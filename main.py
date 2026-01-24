import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant

# --- 🔐 CREDENTIALS (FILLED) ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4Agf2g4JmQDmGNlePOel8m2UfhtsxZMh_gju-prGLyMyGCHuip9-RpjQbKvuwUapQp1nS72s9Ve9Fk0wK7GP4UhEKKtk7JMAax8aif38E5C0X22c3PofLGRWSuAvbkysipyg5N0nS53IC7dKinjuWXCSbZZnOhcQ6EFGUXtIG3XbrDKj7AcV32LUjjMIz6kENhCDnWSOTil3AZNoSlg4a5rUVYgmLiV0LJzeIFsalu9_F-GFEYnCn7R16tQzWe7lcfPznh22XeS8bwOJBh8Hjio8QhKp93XnhTG-4iUlQZoZevVtZKb6KTAwxITYmC12ksXS6Q_Zk6Fpmh9BCmPAjjfgAAAAGc59H6AA"

# --- CONFIGURATION ---
TARGET_BOT_USERNAME = "Backupinfo69_bot" 
SEARCH_GC_ID = "infobot_66"  
NEW_FOOTER = "⚡ Designed & Powered by @MAGMAxRICH"

# Allowed Groups
ALLOWED_GROUPS = [-1003387459132]

# Force Sub Channels
FSUB_CONFIG = [
    {"username": "Anysnapupdate", "link": "https://t.me/Anysnapupdate"},
    {"username": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_gc_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

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

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 **Access Denied!**\nPehle channels join karein.")
    
    text = (
        "📖 **ANYSNAP BOT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **Services:** `/num`, `/vehicle`, `/aadhar`, `/fam`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "vehicle", "aadhar", "familyinfo", "vnum", "fam", "sms"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 **Join Channels First!**")

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    # ✅ ANYSNAP Message
    status_msg = await message.reply_text(f"🔍 **Searching via ANYSNAP...**")
    
    try:
        # 1. GC me request bhejo
        sent_req = await client.send_message(SEARCH_GC_ID, message.text)
        
        target_response = None
        
        # --- WAIT LOOP ---
        for attempt in range(25): 
            await asyncio.sleep(2) 
            
            async for log in client.get_chat_history(SEARCH_GC_ID, limit=20):
                if log.reply_to_message_id == sent_req.id:
                    text_content = (log.text or log.caption or "").lower()
                    
                    # 1. Ignore Wait Messages
                    ignore_words = ["wait", "processing", "searching", "scanning", "loading", "checking"]
                    if any(word in text_content for word in ignore_words):
                        await status_msg.edit(f"⏳ **Fetching Data... (Attempt {attempt+1})**")
                        continue 
                    
                    # 2. Ignore Small Garbage Messages (Footer only messages)
                    if len(text_content) < 40 and not log.media:
                        continue

                    target_response = log
                    break 
            
            if target_response: break
        
        if not target_response:
            await status_msg.edit("❌ **Timeout:** Database se koi response nahi aaya.")
            try:
                await client.delete_messages(SEARCH_GC_ID, sent_req.id)
            except:
                pass
            return

        # --- ✅ DATA SENDING ---
        
        # Priority 1: Text Message
        if target_response.text:
            raw_content = target_response.text
            
            # Unwanted lines hatao
            clean_content = raw_content.replace("@DuXxZx_info", "").replace("Designed & Powered", "")
            
            # Formatting Logic
            if "{" in clean_content and "}" in clean_content:
                final_text = f"```json\n{clean_content}\n```\n\n{NEW_FOOTER}"
            else:
                final_text = f"{clean_content}\n\n{NEW_FOOTER}"

            if len(final_text) > 4000:
                await message.reply_text(final_text[:4000])
                await message.reply_text(final_text[4000:])
            else:
                await message.reply_text(final_text)

        # Priority 2: Media/Photo
        elif target_response.media:
            raw_caption = target_response.caption or ""
            clean_caption = raw_caption.replace("@DuXxZx_info", "").replace("Designed & Powered", "")
            final_caption = f"{clean_caption}\n\n{NEW_FOOTER}"
            
            await target_response.copy(
                chat_id=message.chat.id,
                caption=final_caption[:1024]
            )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print(f"🚀 Secure ANYSNAP Bot connected to @{SEARCH_GC_ID} is Live!")
app.run()
