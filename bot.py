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

# ───────────── BOT CLIENT ───────────── #

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# ───────────── AUTO APPROVE + JOIN UI ───────────── #

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def approve(_, m: Message):
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)

        # Channel link (public/private safe)
        channel_link = (
            f"https://t.me/{m.chat.username}"
            if m.chat.username else None
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔊 Visit Now", url=channel_link)
                ],
                [
                    InlineKeyboardButton(
                        "➕ Add Bot To Channel",
                        url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
                    )
                ]
            ]
        )

        await app.send_message(
            m.from_user.id,
            (
                "🎉 **WELCOME!** 🎉\n\n"
                "✅ **Your join request has been approved successfully.**\n\n"
                f"📢 **Channel:** `{m.chat.title}`\n\n"
                "✨ You can now enjoy all the content."
            ),
            reply_markup=keyboard
        )

        add_user(m.from_user.id)

    except errors.PeerIdInvalid:
        # user ne /start nahi kiya
        pass
    except Exception as e:
        print(e)

# ───────────── /start UI ───────────── #

@app.on_message(filters.private & filters.command("start"))
async def start(_, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                "➕ Aᴅᴅ Tᴏ Cʜᴀɴɴᴇʟ",
                url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
            )],
            [
                InlineKeyboardButton("🗣 Bᴏᴛ Cʜᴀɴɴᴇʟ", url="https://t.me/+33y5cQhKoTQxYTc1"),
                InlineKeyboardButton("👤 Oᴡɴᴇʀ", url="https://t.me/BlacklistedOX")
            ]
        ]
    )

    await m.reply_text(
    (
        "**Wᴇʟᴄᴏᴍᴇ Tᴏ Aᴜᴛᴏ Rᴇǫᴜᴇsᴛ Aᴄᴄᴇᴘᴛ Bᴏᴛ 🤖**\n\n"
        "**I Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Aᴘᴘʀᴏᴠᴇ Tᴏ Aʟʟ Jᴏɪɴ Rᴇǫᴜᴇsᴛs.**\n\n"
        "**⚙️ Hᴏᴡ Tᴏ Usᴇ:**\n"
        "**1️⃣ ➜ Usᴇ Aᴅᴅ Mᴇ Aꜱ Aᴅᴍɪɴ Iɴ Yᴏᴜʀ Cʜᴀɴɴᴇʟ / Gʀᴏᴜᴘ**\n"
        "**2️⃣ 🔐 Gɪᴠᴇ Mᴇ Aᴅᴅ Mᴇᴍʙᴇʀs / Iɴᴠɪᴛᴇ Usᴇʀs Pᴇʀᴍɪssɪᴏɴ**\n\n"
        "**👇 Tᴀᴘ Bᴇʟᴏᴡ Tᴏ Gᴇᴛ Sᴛᴀʀᴛᴇᴅ 🚀**"
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
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except errors.InputUserDeactivated:
            remove_user(user["user_id"])
            deactivated += 1
        except errors.UserIsBlocked:
            blocked += 1
        except Exception:
            failed += 1

    await msg.edit(
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"🚫 Blocked: {blocked}\n"
        f"👻 Deactivated: {deactivated}"
    )

# ───────────── RUN BOT ───────────── #

print("🤖 Auto Approve Bot is Running...")
app.run()