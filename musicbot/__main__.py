import sys
import os
from traceback import print_exc
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import discord
from discord.ext import commands

from config import config
from musicbot import loader
from musicbot.bot import MusicBot
from musicbot.utils import check_dependencies, read_shutdown

# —————— HTTP keep-alive server ——————
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def start_keep_alive_server():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("", port), KeepAliveHandler)
    print(f"🌍 Fake server running on port {port}")
    server.serve_forever()

threading.Thread(target=start_keep_alive_server, daemon=True).start()
# ————————————————————————————————————


initial_extensions = [
    "musicbot.commands.music",
    "musicbot.commands.general",
    "musicbot.commands.developer",
]


intents = discord.Intents.default()
intents.voice_states = True
if config.BOT_PREFIX:
    intents.message_content = True
    prefix = config.BOT_PREFIX
else:
    prefix = " "  # messages can't start with space
if config.MENTION_AS_PREFIX:
    prefix = commands.when_mentioned_or(prefix)

if config.ENABLE_BUTTON_PLUGIN:
    intents.message_content = True
    initial_extensions.append("musicbot.plugins.button")

bot = MusicBot(
    command_prefix=prefix,
    case_insensitive=True,
    status=discord.Status.online,
    activity=discord.Game(name=config.STATUS_TEXT),
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none(),
)


if __name__ == "__main__":
    print("Loading...")

    check_dependencies()
    config.warn_unknown_vars()
    config.save()

    bot.load_extensions(*initial_extensions)

    # start executor before reading from stdin to avoid deadlocks
    loader.init()

    if "--run" in sys.argv:
        shutdown_task = bot.loop.create_task(read_shutdown())

    try:
        bot.run(config.BOT_TOKEN, reconnect=True)
    except discord.LoginFailure:
        print_exc(file=sys.stderr)
        print("Set the correct token in config.json", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        if e.args != ("Event loop is closed",):
            raise
