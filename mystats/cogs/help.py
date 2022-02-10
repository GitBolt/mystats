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
            title="Help is here!",
            color=Colours.DEFAULT.value
        ).add_field(
            name="!lobby `<#channel>` `<meta_data>`",
            value=("Channel and meta data are optional when you use this "
                    "command in game specific channels. When using this "
                    "command from other channel you need to specify the "
                    "game channel and meta data, which is the description of "
                    "the lobby and can have --mode flag to change game mode "
                    "(duos, trios, quads)\nExample: `!lobby #duos --"
                    ),
            inline=False
        ).add_field(
            name="!close",
            value="Use this command to close the lobby you started.",
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
