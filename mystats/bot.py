import os
import disnake
from dotenv import load_dotenv
from disnake.ext import commands

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
    print(f"Logged in as {bot.user}")


print("Loading cogs...")
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(os.environ["TOKEN"])
