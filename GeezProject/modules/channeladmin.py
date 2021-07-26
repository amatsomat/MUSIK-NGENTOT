# Calls Music 1 - Telegram bot for streaming audio in group calls
# Copyright (C) 2021  Roj Serbest

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from asyncio.queues import QueueEmpty
from GeezProject.config import que
from pyrogram import Client, filters
from pyrogram.types import Message

from GeezProject.function.admins import set
from GeezProject.helpers.channelmusic import get_chat_id
from GeezProject.helpers.decorators import authorized_users_only, errors
from GeezProject.helpers.filters import command, other_filters
from GeezProject.services.callsmusic import callsmusic



@Client.on_message(filters.command(["channelpause","cpause"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def pause(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("**Apakah kita terhubung?**")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❗ **Nothing is playing!**")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("▶️ **berhenti berjuang!**")


@Client.on_message(filters.command(["channelresume","cresume"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def resume(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("**Apakah kita terhubung?**")
      return    
    chat_id = chid
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❗ **Tidak ada Lagu yang sedang diputar!**")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ **mulai dari nol!**")


@Client.on_message(filters.command(["channelend","cend"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def stop(_, message: Message):
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("**Apakah kita terhubung?**")
      return    
    chat_id = chid
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ **gada perjuangan yang sia sia!**")
    else:
        try:
            callsmusic.queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("❌ **lagu sudah berhenti berjuang !**")


@Client.on_message(filters.command(["channelskip","cskip"]) & filters.group & ~filters.edited)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    try:
      conchat = await _.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("**Apakah kita terhubung?**")
      return    
    chat_id = chid
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ **gada yg serius!**")
    else:
        callsmusic.queues.task_done(chat_id)

        if callsmusic.queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, callsmusic.queues.get(chat_id)["file"]
            )

        await message.reply_text("⏩ **sabar ya dia udh bahagia !**")


@Client.on_message(filters.command("channeladmincache"))
@errors
async def admincache(client, message: Message):
    try:
      conchat = await client.get_chat(message.chat.id)
      conid = conchat.linked_chat.id
      chid = conid
    except:
      await message.reply("**Apakah kita terhubung?**")
      return
    set(
        chid,
        (
            member.user
            for member in await conchat.linked_chat.get_members(
                filter="administrators"
            )
        ),
    )

    await message.reply_text("✅️ **perjuangan admin** telah **berakhir**")
