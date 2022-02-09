import disnake
from disnake.ext import commands
from models.dropdown import DropdownView

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot,):
        self.bot: commands.Bot = bot

    @commands.command()
    async def avatar(self, ctx: commands.Context):
        view = DropdownView()
        await ctx.send("Sussy", view=view)

def setup(bot):
    bot.add_cog(Help(bot))
