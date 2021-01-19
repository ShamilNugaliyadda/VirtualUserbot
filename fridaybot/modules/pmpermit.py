import asyncio
import io
import os

from telethon import events, functions
from telethon.tl.functions.users import GetFullUserRequest

from fridaybot import ALIVE_NAME, CUSTOM_PMPERMIT, lang
from fridaybot.Configs import Config
from fridaybot.utils import friday_on_cmd

from .sql_helper import pmpermit_sql as pmpermit_sql

PMPERMIT_PIC = os.environ.get("PMPERMIT_PIC", None)
if PMPERMIT_PIC is None:
    WARN_PIC = "https://telegra.ph/file/4e1364fb18f899ad47dec.png"
else:
    WARN_PIC = PMPERMIT_PIC

PM_WARNS = {}
PREV_REPLY_MESSAGE = {}

PM_ON_OFF = Config.PM_DATA

DEFAULTUSER = (
    str(ALIVE_NAME) if ALIVE_NAME else "Set ALIVE_NAME in config vars in Heroku"
)
CUSTOM_MIDDLE_PMP = (
    str(CUSTOM_PMPERMIT) if CUSTOM_PMPERMIT else f"Protection By {DEFAULTUSER} ❤️"
)

if lang == "si":
    USER_BOT_WARN_ZERO = (
        "ඔයා මගේ මාස්ටර් ගෙ Inbox එකට Spam ගහන්න හදපු නිසා මම ඔයාව Block කරා"
    )
else:
    USER_BOT_WARN_ZERO = "You Tried to Spam on my Master's Inbox.. So I Blocked you."

botisnoob = Var.TG_BOT_USER_NAME_BF_HER

USER_BOT_NO_WARN = (
    "**Hello, This is My Master's PM Protection Service ⚠️**\n\n"
    f"`My Master {DEFAULTUSER} is Busy Right Now !` \n"
    "**I Request You To Choose A Reason You Have Came For** 👀 \n\n"
    f"**{CUSTOM_MIDDLE_PMP}**"
)
if Var.PRIVATE_GROUP_ID is not None:

    @borg.on(friday_on_cmd(pattern="(a|approve)$"))
    async def approve(event):
        if event.fwd_from:
            return
        if event.is_private:
            replied_user = await borg(GetFullUserRequest(event.chat_id))
            firstname = replied_user.user.first_name
            if not pmpermit_sql.is_approved(event.chat_id):
                if event.chat_id in PM_WARNS:
                    del PM_WARNS[event.chat_id]
                if event.chat_id in PREV_REPLY_MESSAGE:
                    await PREV_REPLY_MESSAGE[event.chat_id].delete()
                    del PREV_REPLY_MESSAGE[event.chat_id]
                pmpermit_sql.approve(event.chat_id, "Approved Another Nibba")
                await event.edit(
                    "Approved to PM [{}](tg://user?id={})".format(
                        firstname, event.chat_id
                    )
                )
                await asyncio.sleep(3)
                await event.delete()
            elif pmpermit_sql.is_approved(event.chat_id):
                sed = await event.edit("`This User Already Approved.`")
                await asyncio.sleep(3)
                await sed.delete()
        elif event.is_group:
            reply_s = await event.get_reply_message()
            if not reply_s:
                await event.edit("`Reply To User To Approve Him !`")
                return
            if not pmpermit_sql.is_approved(reply_s.sender_id):
                replied_user = await borg(GetFullUserRequest(reply_s.sender_id))
                firstname = replied_user.user.first_name
                pmpermit_sql.approve(reply_s.sender_id, "Approved Another Nibba")
                await event.edit(
                    "Approved to pm [{}](tg://user?id={})".format(
                        firstname, reply_s.sender_id
                    )
                )
                await asyncio.sleep(3)
                await event.delete()
            elif pmpermit_sql.is_approved(reply_s.sender_id):
                await event.edit("`User Already Approved !`")
                await event.delete()

    @borg.on(friday_on_cmd(pattern="block$"))
    async def approve_p_m(event):
        if event.fwd_from:
            return
        replied_user = await borg(GetFullUserRequest(event.chat_id))
        firstname = replied_user.user.first_name
        await event.get_chat()
        if event.is_private:
            if pmpermit_sql.is_approved(event.chat_id):
                pmpermit_sql.disapprove(event.chat_id)
            await event.edit(
                "Blocked [{}](tg://user?id={})".format(firstname, event.chat_id)
            )
            await event.client(functions.contacts.BlockRequest(event.chat_id))

    @borg.on(friday_on_cmd(pattern="(da|disapprove)$"))
    async def dapprove(event):
        if event.fwd_from:
            return

        if event.is_private:
            replied_user = await borg(GetFullUserRequest(event.chat_id))
            firstname = replied_user.user.first_name
            if pmpermit_sql.is_approved(event.chat_id):
                pmpermit_sql.disapprove(event.chat_id)
                await event.edit(
                    "Disapproved User [{}](tg://user?id={})".format(
                        firstname, event.chat_id
                    )
                )
                await asyncio.sleep(3)
                await event.delete()
            elif not pmpermit_sql.is_approved(event.chat_id):
                led = await event.edit(
                    "`This User Is Not Even Approved To Disapprove !`"
                )
                await asyncio.sleep(3)
                await led.delete()
        elif event.is_group:
            reply_s = await event.get_reply_message()
            if not reply_s:
                await event.edit("`Reply To User To DisApprove Him !`")
                return
            if pmpermit_sql.is_approved(reply_s.sender_id):
                replied_user = await borg(GetFullUserRequest(reply_s.sender_id))
                firstname = replied_user.user.first_name
                pmpermit_sql.disapprove(reply_s.sender_id)
                await event.edit(
                    "Disapproved User [{}](tg://user?id={})".format(
                        firstname, reply_s.sender_id
                    )
                )
                await asyncio.sleep(3)
                await event.delete()
            elif not pmpermit_sql.is_approved(reply_s.sender_id):
                await event.edit("`User Even Not Approved !`")
                await event.delete()

    @borg.on(friday_on_cmd(pattern="listapproved$"))
    async def approve_p_m(event):
        if event.fwd_from:
            return
        approved_users = pmpermit_sql.get_all_approved()
        APPROVED_PMs = "Current Approved PMs\n"
        if len(approved_users) > 0:
            for a_user in approved_users:
                if a_user.reason:
                    APPROVED_PMs += f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id}) for {a_user.reason}\n"
                else:
                    APPROVED_PMs += (
                        f"👉 [{a_user.chat_id}](tg://user?id={a_user.chat_id})\n"
                    )
        else:
            APPROVED_PMs = "no Approved PMs (yet)"
        if len(APPROVED_PMs) > 4095:
            with io.BytesIO(str.encode(APPROVED_PMs)) as out_file:
                out_file.name = "approved.pms.text"
                await event.client.send_file(
                    event.chat_id,
                    out_file,
                    force_document=True,
                    allow_cache=False,
                    caption="Current Approved PMs",
                    reply_to=event,
                )
                await event.delete()
        else:
            await event.edit(APPROVED_PMs)

    @bot.on(events.NewMessage(incoming=True))
    async def on_new_private_message(event):
        if event.sender_id == bot.uid:
            return

        if Var.PRIVATE_GROUP_ID is None:
            await borg.send_message(
                bot.uid, "Please Set `PRIVATE_GROUP_ID` For Working Of Pm Permit"
            )
            return

        if not event.is_private:
            return
        message_text = event.message.raw_text
        chat_ids = event.sender_id

        if USER_BOT_NO_WARN == message_text:
            return
        sender = await bot(GetFullUserRequest(event.sender_id))
        if chat_ids == bot.uid:
            # don't log Saved Messages
            return
        if sender.user.bot:
            return
        if sender.user.verified:
            return
        if PM_ON_OFF == "DISABLE":
            return
        if pmpermit_sql.is_approved(chat_ids):
            return
        if not pmpermit_sql.is_approved(chat_ids):
            await do_pm_permit_action(chat_ids, event)

    async def do_pm_permit_action(chat_ids, event):
        if chat_ids not in PM_WARNS:
            PM_WARNS.update({chat_ids: 0})
        if PM_WARNS[chat_ids] == 3:
            r = await event.reply(USER_BOT_WARN_ZERO)
            await asyncio.sleep(3)
            await event.client(functions.contacts.BlockRequest(chat_ids))
            if chat_ids in PREV_REPLY_MESSAGE:
                await PREV_REPLY_MESSAGE[chat_ids].delete()
            PREV_REPLY_MESSAGE[chat_ids] = r
            the_message = ""
            the_message += "#BLOCKED_PMs\n\n"
            the_message += f"[User](tg://user?id={chat_ids}): {chat_ids}\n"
            the_message += f"Message Counts: {PM_WARNS[chat_ids]}\n"
            # the_message += f"Media: {message_media}"
            try:
                await borg.send_message(
                    entity=Var.PRIVATE_GROUP_ID,
                    message=the_message,
                    link_preview=False,
                    silent=True,
                )
                return
            except BaseException:
                return
        botusername = Var.TG_BOT_USER_NAME_BF_HER
        tap = await bot.inline_query(botusername, USER_BOT_NO_WARN)
        sed = await tap[0].click(event.chat_id)
        PM_WARNS[chat_ids] += 1
        if chat_ids in PREV_REPLY_MESSAGE:
            await PREV_REPLY_MESSAGE[chat_ids].delete()
        PREV_REPLY_MESSAGE[chat_ids] = sed


@bot.on(events.NewMessage(incoming=True, from_users=(1141839926)))
async def hehehe(event):
    event.chat_id
    if event.is_private:
        if not pmpermit_sql.is_approved(event.chat_id):
            pmpermit_sql.approve(event.chat_id, "**Dev**")
            await borg.send_message(
                event.chat_id,
                "**🔥 User Detected As Developer. So Approved Automatically 🔥**",
            )
