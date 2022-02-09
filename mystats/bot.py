import os
import disnake
from dotenv import load_dotenv
from disnake.ext import commands
from logger import log

load_dotenv()

intents = disnake.Intents().all()

bot: commands.Bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    intents=intents
)

@bot.event
async def on_ready() -> None:
    await bot.change_presence(
        activity=disnake.Activity(
            type=disnake.ActivityType.streaming,
            name=f"Enter !help for help"
        ))
    log.info(f"Logged in as {bot.user}")


log.info("Loading cogs...")
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
log.success("Loaded cogs")


bot.run(os.environ["TOKEN"])
