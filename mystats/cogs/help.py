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
            name=("Looking for a game? See below for instructions to "
                  "create a lobby and connect with other players."),
            value=("> __How to CREATE a LOBBY?__\n"
                   "> 1. Go to the game channel of your desired game type. "
                   "(Example: Warzon Duo's, Fornite Trio's)\n"
                   "> 2. Type !lobby create\n"
                   "> 3. Optionally provide the lobby description "
                   "(after the word create in command) "
                   "Example: !lobby create looking for a quick match\n"
                   "> 4. A MESSAGE will be sent with the lobby information "
                   "and buttons using which people can join\n"
                   "> 5. Join Your Lobby Voice Channel / Type in Lobby "
                   "Text Channel to communicate withyour new teammates  "
                   "(located in LOBBIES discord category)\n\n"
                   "> __How to JOIN a LOBBY?__\n"
                   "> 1. Click on desired game type channel "
                   "(Warzon Duo's, Fornite Trio's, etc...)\n"
                   "> 2. Click on the 'JOIN' button in the lobby of your choice\n"
                   "> 3. Join Lobbies Voice Channel / Type in Lobby Text Channel "
                   "to communicate with your new teammates "
                   "(look for Lobby Leaders name)\n\n"
                   "> __How to leave a LOBBY?__\n"
                   "> 1. Type !lobby leave\n"
                   "> 2. Your slot will become free and your name will "
                   "be removed from the embed\n"
                   "> 3. Type !lobby close to close the lobby YOU created.\n"
                   ),
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
