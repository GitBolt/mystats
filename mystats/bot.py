import os
import disnake
from dotenv import load_dotenv
from disnake.ext import commands

load_dotenv()
intents = disnake.Intents().all()

bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    intents=intents
)

bot.run(os.environ("TOKEN"))
