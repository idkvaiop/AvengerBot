import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait

from Avenger import BOT_ID, BOT_NAME, SUDOERS, app
from Avenger.core.decorators.errors import capture_err
from Avenger.modules import ALL_MODULES
from Avenger.utils.dbfunctions import (
    get_blacklist_filters_count,
    get_filters_count,
    get_gbans_count,
    get_karmas_count,
    get_notes_count,
    get_rss_feeds_count,
    get_served_chats,
    get_served_users,
    get_warns_count,
    remove_served_chat,
)
from Avenger.utils.http import get
from Avenger.utils.inlinefuncs import keywords_list


@app.on_message(filters.command("clean_db") & filters.user(SUDOERS))
@capture_err
async def clean_db(_, message):
    served_chats = [int(i["chat_id"]) for i in (await get_served_chats())]
    m = await message.reply(
        f"__**Cleaning database, Might take around {len(served_chats)*2} seconds.**__",
    )
    for served_chat in served_chats:
        try:
            await app.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
    await m.edit("**Database Cleaned.**")


@app.on_message(filters.command("gstats") & filters.user(SUDOERS))
@capture_err
async def global_stats(_, message):
    m = await app.send_message(
        message.chat.id,
        text="__**Analysing Stats...**__",
        disable_web_page_preview=True,
    )

    # For bot served chat and users count
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    # Gbans count
    gbans = await get_gbans_count()
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Blacklisted filters count across chats
    _filters = await get_blacklist_filters_count()
    blacklist_filters_count = _filters["filters_count"]
    blacklist_filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # Contributors/Developers count and commits on github
    url = "https://api.github.com/repos/TeamAvengerBot/AvengerBot/contributors"
    rurl = "https://github.com/TeamAvengerBot/AvengerBot"
    developers = await get(url)
    commits = sum(developer["contributions"] for developer in developers)
    developers = len(developers)

    # Rss feeds
    rss_count = await get_rss_feeds_count()
    # Modules info
    modules_count = len(ALL_MODULES)

    # Userbot info
    groups_ub = channels_ub = bots_ub = privates_ub = total_ub = 0

    msg = f"""
** Akira Global Status **
**Total Modules** : {modules_count}
**Inline Modules** : {len(keywords_list)}
**Total Users** : {served_users}
**Total Chats** : {served_chats}
**Total Notes** : {notes_count}
**Total Filters** : {filters_count}
**Total Warns** : {warns_count}
**Total Karma** : {karmas_count}
**Total Gbans** : {gbans}
**RSS Feeds** : {rss_count}
**Blacklisted** : {blacklist_filters_count}
**Devs** : {developers}
**Creator** : [Akhil 🇮🇳](tg://user?id={2102783671})

© @THERADION
"""
    await m.edit(msg, disable_web_page_preview=True)
