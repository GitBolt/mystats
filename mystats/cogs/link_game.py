import os
from typing import Any
from disnake import Embed
from disnake.ext import commands
from constants import Colours


class LinkGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, invoke_without_command=True)
    async def link(self, ctx: commands.Context) -> None:
        await ctx.invoke(self.bot.get_command('help'))

    @link.command()
    async def game(
            self,
            ctx: commands.Context,
            game: str,
            id: str,
            platform: str
            ) -> None:
        pass


def setup(bot):
    bot.add_cog(LinkGame(bot))
