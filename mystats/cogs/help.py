import disnake
from disnake.ext import commands
from disnake import Embed
from constants import Colours


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot,):
        self.bot: commands.Bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context) -> None:
        embed: Embed = Embed(
            title="Welcome to MYSTATS LOBBY CREATOR",
            color=Colours.DEFAULT.value
        ).add_field(
            name="!lobby create",
            value=("\n> __How to create a LOBBY?__\n"
                   "> 1. Go to the channel where you want to start the lobby\n"
                   "> 2. Enter `!lobby create`\n"
                   "> 3. Optionally provide the lobby description. "
                   "For example `!lobby create looking for a quick match`\n"
                   "> 4. An embed will be sent with the lobby information and buttons using which people can join\n\n"
                   "> __How to join a LOBBY?__\n"
                   "> 1. Make sure you are not the lobby leader\n"
                   "> 2. Go the game channel to find any open lobby\n"
                   "> 3. Click on 'Join' button in the lobby embed\n"
                   "> 4. You will be added to the lobby and embed will show your name\n\n"
                   "> __How to leave a LOBBY?__\n"
                   "> 1. Make sure you are in a lobby\n"
                   "> 2. Make sure you are not the lobby leader\n"
                   "> 3. Find your lobby's embed in your game channel and click on 'Leave' button\n"
                   "> 4. Your slot will become free and your name will be removed from the embed"
                   ),
            inline=False
        ).add_field(
            name="!lobby close",
            value="Use this command to close the lobby you started.",
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
