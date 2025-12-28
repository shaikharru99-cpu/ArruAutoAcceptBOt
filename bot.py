import asyncio
from pyrogram import Client, filters, errors
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.flood_420 import FloodWait

from configs import cfg
from database import (
    add_user,
    add_group,
    all_users,
    all_groups,
    users,
    remove_user
)
import logging

# ───────────── LOGGING SETUP ───────────── #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ───────────── BOT CLIENT ───────────── #

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# ───────────── AUTO APPROVE + JOIN UI ───────────── #

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m):
    try:
        # Add group to database
        add_group(m.chat.id)
        
        # Approve the join request
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)
        
        # Add user to database
        add_user(m.from_user.id)
        
        # Get channel link
        channel_link = (
            f"https://t.me/{m.chat.username}"
            if m.chat.username 
            else f"https://t.me/c/{str(m.chat.id)[4:] if str(m.chat.id).startswith('-100') else m.chat.id}"
        )
        
        # Prepare keyboard
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔊 Visit Channel", url=channel_link)],
                [InlineKeyboardButton(
                    "🤖 Add Bot To Your Channel",
                    url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
                )]
            ]
        )

        # Send welcome message to user with error handling
        try:
            await app.send_message(
                m.from_user.id,
                (
                    "🎉 **WELCOME TO MY OWNER CHANNEL** 🎉\n\n"
                    "You have successfully joined the channel through my owner bot.\n\n"
                    "✅ **Your request has been accepted.**\n"
                    "You are now officially a member of our channel.\n\n"
                    "✨ Enjoy and explore all the content here 😊"
                ),
                reply_markup=keyboard
            )
            logger.info(f"Welcome message sent to user {m.from_user.id}")
            
        except errors.UserIsBlocked:
            logger.warning(f"User {m.from_user.id} has blocked the bot")
            
        except errors.PeerIdInvalid:
            logger.warning(f"PeerIdInvalid for user {m.from_user.id}")
            
        except errors.FloodWait as e:
            logger.warning(f"Flood wait for {e.value} seconds for user {m.from_user.id}")
            await asyncio.sleep(e.value)
            
        except Exception as e:
            logger.error(f"Failed to send PM to user {m.from_user.id}: {e}")

    except errors.FloodWait as e:
        logger.warning(f"Flood wait in approve function: {e.value} seconds")
        await asyncio.sleep(e.value)
        
    except Exception as e:
        logger.exception(f"Error in approve function: {e}")

# ───────────── LEAVE MESSAGE ───────────── #

@app.on_chat_member_updated()
async def handle_leave(_, update):
    try:
        # Check if user left
        if update.old_chat_member and update.new_chat_member:
            if (update.old_chat_member.status in [
                ChatMemberStatus.MEMBER, 
                ChatMemberStatus.ADMINISTRATOR, 
                ChatMemberStatus.OWNER
            ] and update.new_chat_member.status == ChatMemberStatus.LEFT):
                
                user_id = update.new_chat_member.user.id
                chat_id = update.chat.id
                
                try:
                    await app.send_message(
                        user_id,
                        "😢 **You left the channel!**\n\n"
                        "We're sad to see you go. If you change your mind, "
                        "you can always rejoin through the link:\n\n"
                        f"https://t.me/c/{str(chat_id)[4:] if str(chat_id).startswith('-100') else chat_id}"
                    )
                    logger.info(f"Leave message sent to user {user_id}")
                    
                except errors.UserIsBlocked:
                    logger.warning(f"User {user_id} has blocked the bot (leave message)")
                except Exception as e:
                    logger.error(f"Failed to send leave message to {user_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in handle_leave: {e}")

# ───────────── /start UI ───────────── #

@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                "➕ Add To Channel",
                url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
            )],
            [
                InlineKeyboardButton("🗣 Bot Channel", url="https://t.me/+33y5cQhKoTQxYTc1"),
                InlineKeyboardButton("👤 Owner", url="https://t.me/BlacklistedOX")
            ]
        ]
    )

    await m.reply_text(
        (
            "**Welcome To Auto Request Accept Bot 🤖**\n\n"
            "**I Automatically Approve All Join Requests.**\n\n"
            "**⚙️ How To Use:**\n"
            "**1️⃣ ➜ Add Me As Admin In Your Channel / Group**\n"
            "**2️⃣ 🔐 Give Me Add Members / Invite Users Permission**\n\n"
            "**👇 Tap Below To Get Started 🚀**"
        ),
        reply_markup=keyboard
    )
    
    add_user(m.from_user.id)

# ───────────── USERS STATS (ADMIN ONLY) ───────────── #

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def stats(_, m: Message):
    u = all_users()
    g = all_groups()
    await m.reply_text(
        f"📊 **BOT STATISTICS**\n\n"
        f"👤 Users: `{u}`\n"
        f"👥 Groups: `{g}`\n"
        f"📦 Total: `{u + g}`"
    )

# ───────────── BROADCAST (ALL MEDIA, REPLY) ───────────── #

@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def broadcast(_, m: Message):
    if not m.reply_to_message:
        return await m.reply_text("❌ Reply to a message to broadcast.")

    msg = await m.reply_text("⚡ Broadcasting...")
    success = failed = blocked = deactivated = 0

    for user in users.find():
        try:
            await m.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.05)  # Small delay to avoid flood
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except errors.InputUserDeactivated:
            remove_user(user["user_id"])
            deactivated += 1
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            logger.error(f"Failed to send to {user['user_id']}: {e}")
            failed += 1

    await msg.edit(
        f"📊 **Broadcast Results**\n\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`\n"
        f"🚫 Blocked: `{blocked}`\n"
        f"👻 Deactivated: `{deactivated}`"
    )

# ───────────── RUN BOT ───────────── #

if __name__ == "__main__":
    print("🤖 Auto Approve Bot is Running...")
    app.run()