import sys
import time
import asyncio
import threading
from datetime import date, datetime
from pathlib import Path
import importlib.util
import requests
import pytz
from aiohttp import web
from PIL import Image 
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
import pyrogram.utils
from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium
from Lucia.Bot import SilentX
from Lucia.util.keepalive import ping_server
from Lucia.Bot.clients import initialize_clients
from logging_helper import LOGGER

botStartTime = time.time()

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647

def ping_loop():
    while True:
        try:
            r = requests.get(URL, timeout=10)
            if r.status_code == 200:
                LOGGER.info("✅ Ping Successful")
            else:
                LOGGER.error(f"⚠️ Ping Failed: {r.status_code}")
        except Exception as e:
            LOGGER.error(f"❌ Exception During Ping: {e}")
        time.sleep(120)


if URL:
    threading.Thread(target=ping_loop, daemon=True).start()


def silentx_plugins_handler(app, plugins_dir: str | Path = "plugins", package_name: str = "plugins") -> list[str]:
    plugins_dir = Path(plugins_dir)
    loaded_plugins: list[str] = []

    if not plugins_dir.exists():
        LOGGER.warning("Plugins Directory '%s' Does Not Exist.", plugins_dir)
        return loaded_plugins

    for file in sorted(plugins_dir.rglob("*.py")):
        if file.name == "__init__.py":
            continue

        rel_path = file.relative_to(plugins_dir).with_suffix("")
        import_path = package_name + ".".join([""] + list(rel_path.parts))

        try:
            spec = importlib.util.spec_from_file_location(import_path, file)
            if spec is None or spec.loader is None:
                LOGGER.warning("Skipping %s (No Spec/Loader).", file)
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            loaded_plugins.append(import_path)

            short_name = import_path.removeprefix(f"{package_name}.")
            LOGGER.info("🔌 Loaded plugin: %s", short_name)

        except Exception:
            LOGGER.exception("Failed To Import Plugin: %s", import_path)

    disp = getattr(app, "dispatcher", None)
    if disp is None:
        LOGGER.warning("App Has No Dispatcher; Skipping Handler Regroup.")
        return loaded_plugins

    if 0 in disp.groups:
        all_handlers = list(disp.groups[0])
        for i, handler in enumerate(all_handlers):
            disp.remove_handler(handler, group=0)
            disp.add_handler(handler, group=i)
    else:
        LOGGER.info("No Handlers In Group 0; Nothing To Regroup.")

    return loaded_plugins


async def SilentXBotz_start():
    if MULTIPLE_DB and not DATABASE_URI2:
        LOGGER.error("DATABASE_URI2 Is Not Provided But MULTIPLE_DB Is Set To True. Please Fill The DATABASE_URI2 Var!")
        sys.exit(1)
    if not API_ID or not API_HASH or not BOT_TOKEN:
        LOGGER.error("Missing required environment variables (API_ID, API_HASH, or BOT_TOKEN)")
        sys.exit(1)

    LOGGER.info("Initializing Your Bot!")
    await SilentX.start()
    bot_info = await SilentX.get_me()
    SilentX.username = bot_info.username
    await initialize_clients()
    loaded_plugins = silentx_plugins_handler(SilentX)
    if loaded_plugins:
        LOGGER.info("✅ Plugins Loaded: %d", len(loaded_plugins))
    else:
        LOGGER.info("⚠️ No Plugins Loaded.")
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
    except Exception as e:
        LOGGER.error(f"Error fetching banned users/chats: {e}")
    try:
        await Media.ensure_indexes()
        if MULTIPLE_DB:
            await Media2.ensure_indexes()
        if MULTIPLE_DB:
            LOGGER.info("Multiple Database Mode On. Now Files Will Be Saved In Second DB If First DB Is Full")
        else:
            LOGGER.info("Single DB Mode On! Files Will Be Saved In First Database")
    except Exception as e:
        LOGGER.error(f"Error ensuring indexes: {e}")
    me = await SilentX.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    SilentX.username = "@" + me.username
    SilentX.loop.create_task(check_expired_premium(SilentX))
    LOGGER.info(
        "%s with Pyrofork v%s (Layer %s) started on @%s.",
        me.first_name,
        __version__,
        layer,
        me.username,
    )
    LOGGER.info(script.LOGO)
    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    try:
        await SilentX.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(temp.B_LINK, today, time_str),
        )
    except Exception as e:
        LOGGER.error(f"Error Sending Restart Log: {e}")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()

    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(SilentXBotz_start())
    except KeyboardInterrupt:
        LOGGER.info("Service Stopped Bye 👋")
