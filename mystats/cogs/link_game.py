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
            game_name: str = None,
            player_id: str = None,
            platform: str = None
    ) -> None:
        if not game_name or not player_id or not platform:
            return await ctx.send("You need to provide the game name, id and platform")

        platforms = ["uno", "psn", "xbox", "battle"]
        if platform.lower() not in platforms:
            return await ctx.send("Platform not supported")

        db = self.bot.mongo_client["LinkGame"]
        user_collection = db[str(ctx.author.id)]
        
        existing_data = await user_collection[platform].find_one({"game": game_name, "id": player_id})
        if existing_data:
            return await ctx.send("You have already linked the game with the id and platform")
        await user_collection[platform].insert_one({"game": game_name, "id": player_id})
        await ctx.send("Successfully linked game")

def setup(bot):
    bot.add_cog(LinkGame(bot))
