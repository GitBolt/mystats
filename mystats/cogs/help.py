import disnake
from disnake.ext import commands
from disnake import Embed
from constants import Colours


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot,):
        self.bot: commands.Bot = bot

    @commands.command()
    async def help(self, ctx: commands.Context):
        embed: Embed = Embed(
            title="Help is here!",
            color=Colours.DEFAULT.value
        ).add_field(
            name="!lobby `<#channel>` `<meta_data>`",
            value=("Meta data contains the lobby's description where you can "
                   "use `--players` and `--timeout` flags to change the default "
                   " values.\nDefault players are 4 and timeout is 30 minutes"
                   ),
            inline=False
        ).add_field(
            name="!close",
            value="Use this command to close the lobby you started",
            inline=False
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))
