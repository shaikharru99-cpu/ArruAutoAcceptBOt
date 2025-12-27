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

@app.on_chat_join_request(filters.group | filters.channel)
async def approve(_, m: Message):
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)
        add_user(m.from_user.id)

        channel_link = (
            f"https://t.me/{m.chat.username}"
            if m.chat.username else None
        )

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔊 Visit Channel", url=channel_link)],
                [InlineKeyboardButton(
                    "🤖 Add Bot To Your Channel",
                    url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
                )]
            ]
        )

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

    except errors.PeerIdInvalid:
        pass
    except Exception:
        pass

# ───────────── LEAVE UI ───────────── #

@app.on_chat_member_updated(filters.group | filters.channel)
async def leave_handler(_, cmu):
    try:
        if (
            cmu.old_chat_member.status in
            [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]
            and cmu.new_chat_member.status == ChatMemberStatus.LEFT
        ):
            channel_link = (
                f"https://t.me/{cmu.chat.username}"
                if cmu.chat.username else None
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔄 Rejoin Channel", url=channel_link)],
                    [InlineKeyboardButton(
                        "🤖 Add Bot To Your Channel",
                        url=f"https://t.me/{(await app.get_me()).username}?startchannel=true"
                    )]
                ]
            )

            await app.send_message(
                cmu.from_user.id,
                (
                    "⚠️ **YOU LEFT THE CHANNEL** ⚠️\n\n"
                    "It looks like you left our channel.\n\n"
                    "If this was a mistake or you want to rejoin,\n"
                    "click the button below 👇\n\n"
                    "**Channel link is given below – please join again.**"
                ),
                reply_markup=keyboard
            )
    except Exception:
        pass

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
                InlineKeyboardButton("📢 Bot Channel", url="https://t.me/VJ_Botz"),
                InlineKeyboardButton("👤 Owner", url="https://t.me/KingVJ01")
            ]
        ]
    )

    await m.reply_text(
        (
            "🎉🎊 **WELCOME TO AUTO APPROVE BOT** 🎊🎉\n\n"
            "**🤖 WHAT I DO**\n"
            "• Automatically approve pending join requests\n"
            "• Works in Channels & Groups\n\n"
            "**⚙️ HOW TO USE**\n"
            "1️⃣ Add me to your Channel / Group\n"
            "2️⃣ Promote me as Admin\n"
            "3️⃣ Enable Add Members permission\n\n"
            "🚀 **That’s it!**\n"
            "All join requests will be approved automatically."
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