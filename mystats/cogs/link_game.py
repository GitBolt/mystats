import os
from typing import Any
from disnake import Embed
from disnake.ext import commands
from constants import Colours


SUPPORTED_GAMES: tuple[str, str, str, str] = (
    "warzone",
    "fortnite",
    "apex",
    "halo"
)

class LinkGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, invoke_without_command=True)
    async def link(self, ctx: commands.Context) -> None:
        pass

    @link.command()
    async def game(
            self,
            ctx: commands.Context,
            player_id: str = None,
            platform: str = None
    ) -> None:
        if not player_id or not platform:
            return await ctx.send("You need to provide the id and platform")

        channel_name = ctx.channel.category.name.lower()
        game_list = [i for i in SUPPORTED_GAMES if i in channel_name]
        game_name = None
        if game_list:
            game_name: str = game_list[0].lower()
        else:
            return await ctx.send("Unsupported channel, make sure you are in a game category.")

        platforms = ["acti", "psn", "xbox", "battle", "origin", "riot", "epic", "steam"]
        if len(platform.split()) > 1:
            return await ctx.send("Invalid format, enter the command in the following way:\n```!link game <id> <platform>```")
        if platform.lower() not in platforms:
            return await ctx.send("Platform not supported. Enter one of these - acti, psn, xbox, battle, origin, riot, epic and steam")
        
        db = self.bot.mongo_client["LinkGame"]
        user_collection = db[str(ctx.author.id)]
        
        existing_data = await user_collection[platform].find_one({"game": game_name, "id": player_id})
        if existing_data:
            return await ctx.send("You have already linked the game with the id and platform")
        await user_collection[platform].insert_one({"game": game_name, "id": player_id})
        await ctx.send("Successfully linked game")

    @link.command()
    async def remove(
            self,
            ctx: commands.Context,
            player_id: str = None,
            platform: str = None
    ) -> None:
        if not player_id or not platform:
            return await ctx.send("You need to provide the id and platform")

        channel_name = ctx.channel.category.name.lower()
        game_list = [i for i in SUPPORTED_GAMES if i in channel_name]
        game_name = None
        if game_list:
            game_name: str = game_list[0].lower()
        else:
            return await ctx.send("Unsupported channel, make sure you are in a game category.")

        platforms = ["acti", "psn", "xbox", "battle", "origin", "riot", "epic", "steam"]
        if len(platform.split()) > 1:
            return await ctx.send("Invalid format, enter the command in the following way:\n```!link game <id> <platform>```")
        if platform.lower() not in platforms:
            return await ctx.send("Platform not supported. Enter one of these - acti, psn, xbox, battle, origin, riot, epic and steam")
        
        db = self.bot.mongo_client["LinkGame"]
        user_collection = db[str(ctx.author.id)]
        
        existing_data = await user_collection[platform].find_one({"game": game_name, "id": player_id})
        if not existing_data:
            return await ctx.send("You have not linked the game with the id and platform")
        await user_collection[platform].delete_one(existing_data)
        await ctx.send("Successfully removed linked game")

def setup(bot):
    bot.add_cog(LinkGame(bot))