import os
from logger import log
from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from disnake.ext import commands
from disnake import Intents, Activity, ActivityType

load_dotenv()

intents: Intents = Intents().all()

bot: commands.Bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    intents=intents
)


@bot.event
async def on_ready() -> None:
    log.info(f"Changing presence...")
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.streaming,
            name=f"Enter !help for help"
        ))
    bot.request_client = ClientSession()
    bot.mongo_client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    log.success(f"Logged in as {bot.user}")


log.info("Loading cogs...")
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
log.success("Loaded cogs")


bot.run(os.environ["TOKEN"])
