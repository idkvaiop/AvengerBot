import asyncio
import importlib
import re
from contextlib import closing, suppress

from pyrogram import enums, filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from uvloop import install

from Avenger import BOT_NAME, BOT_USERNAME, LOG_GROUP_ID, aiohttpsession, app
from Avenger.modules import ALL_MODULES
from Avenger.modules.sudoers import bot_sys_stats
from Avenger.utils import paginate_modules
from Avenger.utils.constants import MARKDOWN
from Avenger.utils.dbfunctions import clean_restart_stage

loop = asyncio.get_event_loop()

HELPABLE = {}


async def start_bot():
    global HELPABLE

    for module in ALL_MODULES:
        imported_module = importlib.import_module(f"Avenger.modules.{module}")
        if (
            hasattr(imported_module, "__MODULE__")
            and imported_module.__MODULE__
        ):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (
                hasattr(imported_module, "__HELP__")
                and imported_module.__HELP__
            ):
                HELPABLE[imported_module.__MODULE__.lower()] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
    print(f"[AVENGER]: BOT STARTED AS {BOT_NAME}!")

    restart_data = await clean_restart_stage()

    try:
        print("[AVENGER]: SENDING ONLINE STATUS")
        if restart_data:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "**Restarted Successfully**",
            )

        else:
            await app.send_message(LOG_GROUP_ID, "Bot started!")
    except Exception:
        pass

    await idle()

    await aiohttpsession.close()
    print("[AVENGER]: CLOSING AIOHTTP SESSION AND STOPPING BOT")
    await app.stop()
    print("[AVENGER]: Bye!")
    for task in asyncio.all_tasks():
        task.cancel()
    print("[AVENGER]: Turned off!")


home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Add Me To Serve You!", url=f"http://t.me/{BOT_USERNAME}?startgroup=new"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Help", callback_data="bot_commands",
            ),
            InlineKeyboardButton(
                text="Info", callback_data="akira_info",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Updates",
                url="t.me/THERADION",
            ),
            InlineKeyboardButton(
                text="Support",
                url="t.me/RADIONSUPPORT",
            ),
        
        ],
    ]
)

home_text_pm = (
    f"Hey! I am [**Akira**](https://telegra.ph/file/2079b686ea131a7bda2cd.jpg)."
    + "I can manage your group with lots of useful features..!!! "
    + "If you are searching for the safest bot, Akira is the right option for you."
    + "☆━━━━━━━━━━━━━━━━☆ "
    + "__I have all basic Admin Modules And All Advanced Modules to suite all your needs... Give me a chance I promise no one can defeat my features.__"
)


keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="Help",
                callback_data=bot_commands",
            ),
            InlineKeyboardButton(
                text="Stats",
                callback _data=stats_callback",
            ),
        ],
        [
            InlineKeyboardButton(
                text="My Creator",
                url="t.me/akhilprs",
            ),
        ],
    ]
)


@app.on_message(filters.command("start"))
async def start(_, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply_photo(
            photo="https://telegra.ph/file/2079b686ea131a7bda2cd.jpg",
            caption="PM Me for more detailed information.",
            reply_markup=keyboard,
        )
    if len(message.text.split()) > 1:
        name = (message.text.split(None, 1)[1]).lower()
        if name == "mkdwn_help":
            await message.reply(
                MARKDOWN, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True
            )
        elif "_" in name:
            module = name.split("_", 1)[1]
            text = (
                f"Here is the help for **{HELPABLE[module].__MODULE__}**:\n"
                + HELPABLE[module].__HELP__
            )
            await message.reply(text, disable_web_page_preview=True)
        elif name == "help":
            text, keyb = await help_parser(message.from_user.first_name)
            await message.reply(
                text,
                reply_markup=keyb,
            )
    else:
        await message.reply_photo(
            photo="https://telegra.ph/file/2079b686ea131a7bda2cd.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
    return


@app.on_message(filters.command("help"))
async def help_command(_, message):
    if message.chat.type != enums.ChatType.PRIVATE:
        if len(message.command) >= 2:
            name = (message.text.split(None, 1)[1]).lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Click here",
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await message.reply(
                    f"Click on the below button to get help about {name}",
                    reply_markup=key,
                )
            else:
                await message.reply(
                    "PM Me For More Details.", reply_markup=keyboard
                )
        else:
            await message.reply(
                "Pm Me For More Details.", reply_markup=keyboard
            )
    elif len(message.command) >= 2:
        name = (message.text.split(None, 1)[1]).lower()
        if str(name) in HELPABLE:
            text = (
                f"Here is the help for **{HELPABLE[name].__MODULE__}**:\n"
                + HELPABLE[name].__HELP__
            )
            await message.reply(text, disable_web_page_preview=True)
        else:
            text, help_keyboard = await help_parser(
                message.from_user.first_name
            )
            await message.reply(
                text,
                reply_markup=help_keyboard,
                disable_web_page_preview=True,
            )
    else:
        text, help_keyboard = await help_parser(message.from_user.first_name)
        await message.reply(
            text, reply_markup=help_keyboard, disable_web_page_preview=True
        )
    return


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        """Hey {first_name}, I am {bot_name} !
I'm a group management bot with some useful features.

I am less stress free to setup and can manage your groups hassle free without
giving you much load...!!!
If you face any problem, make sure to connect with us at @RADIONSUPPORT.
""".format(
            first_name=name,
            bot_name=BOT_NAME,
        ),
        keyboard,
    )


@app.on_callback_query(filters.regex("bot_commands"))
async def commands_callbacc(_, CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await app.send_message(
        CallbackQuery.message.chat.id,
        text=text,
        reply_markup=keyboard,
    )

    await CallbackQuery.message.delete()


@app.on_callback_query(filters.regex("akira_info"))
async def stats_callbacc(_, CallbackQuery):
    text = """
Hey !
I am **Akira** !
I am a Super Powerful Group Management Bot to manage your groups..!!!

𝗦𝗼𝗺𝗲 𝗼𝗳 𝘁𝗵𝗲 𝗡𝗼𝘁𝗮𝗯𝗹𝗲 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗼𝗳 𝗔𝗸𝗶𝗿𝗮 :

✪ Music Player.
✪ Fast and Responsive.
✪ Quotely.
✪ Shippering.
✪ AI Based Modules.
"""
    await CallbackQuery.message.delete()


@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)
    top_text = f"""
Hello {query.from_user.first_name}, My name is {BOT_NAME}.
I'm a group management bot with some usefule features.

I am less stress free to setup and can manage your groups hassle free without
giving you much load...!!!
If you face any problem, make sure to connect with us at @RADIONSUPPORT.
 """
    if mod_match:
        module = mod_match.group(1)
        text = (
            "{} **{}**:\n".format(
                "Here is the help for", HELPABLE[module].__MODULE__
            )
            + HELPABLE[module].__HELP__
        )

        await query.message.edit(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("back", callback_data="help_back")]]
            ),
            disable_web_page_preview=True,
        )
    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
        await query.message.delete()
    elif prev_match:
        curr_page = int(prev_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page - 1, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page + 1, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif create_match:
        text, keyboard = await help_parser(query)
        await query.message.edit(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    return await client.answer_callback_query(query.id)


if __name__ == "__main__":
    install()
    with closing(loop):
        with suppress(asyncio.exceptions.CancelledError):
            loop.run_until_complete(start_bot())
        loop.run_until_complete(asyncio.sleep(3.0))  # task cancel wait
