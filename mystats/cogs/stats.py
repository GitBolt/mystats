import os
from typing import Any
from disnake import Embed
from disnake.ext import commands
from constants import Colours


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endpoint = ("https://mystats-rest-api-dot-my-stats"
                         "-326609.uc.r.appspot.com/player")

    @commands.command()
    async def stats(self,
                    ctx: commands.Context,
                    player_username: str = None,
                    platform: str = None,
                    game: str = "warzone"
                    ) -> None:
        if player_username is None or platform is None:
            return await ctx.send("You need to enter player Id and platoform")

        platforms = ["uno", "psn", "xbox", "battle"]
        data: dict[str, str] = {
            "playerUsername": player_username,
            "playerPlatform": platform,
            "playerGame": game
        }
        if platform not in platforms:
            return await ctx.send(
                "Platform not supported. Enter one of these - uno, psn, xbox, battle"
            )

        res_data: dict[str, Any] = None

        async with self.bot.request_client.post(
            self.endpoint,
            headers={"Authorisation": os.environ["API_KEY"]},
            json=data
        ) as res:
            if res.status == 404:
                return await ctx.send(f"Could not find **{player_username}** on **{platform.capitalize()}**")
            res_data = await res.json()

        overall = res_data["overall"]
        last20 = res_data["last20Matches"]

        embed: Embed = Embed(
            title=f"Stats for {res_data['username']}",
            color=Colours.SUCCESS.value
        ).add_field(
            name="** **",
            value="> **OVERALL**",
            inline=False
        ).add_field(
            name="Wins",
            value=overall["wins"]
        ).add_field(
            name="Kills",
            value=overall["kills"]
        ).add_field(
            name="KD Ratio",
            value=str(round(overall["kdRatio"], 3)) + "%"
        ).add_field(
            name="Games played",
            value=overall["gamesPlayed"]
        ).add_field(
            name="Win percent",
            value=str(round(overall["winPercentage"], 3)) + "%"
        ).add_field(
            name="Deaths",
            value=overall["deaths"]

        ).add_field(
            name="** **",
            value="> **LAST 20 MATCHES**",
            inline=False
        ).add_field(
            name="Kills",
            value=last20["kills"]
        ).add_field(
            name="KD Ratio",
            value=str(round(last20["kdRatio"], 3)) + "%"
        ).add_field(
            name="Games played",
            value=last20["gamesPlayed"]
        ).add_field(
            name="Gulag KD",
            value=str(round(last20["gulagKd"], 3))
        ).add_field(
            name="Damage done",
            value=last20["damageDone"]
        ).add_field(
            name="Kills per game",
            value=last20["killsPerGame"]
        ).add_field(
            name="Average life time",
            value=round(last20["avgLifeTime"], 3)
        ).set_footer(text=f"Game: {game.capitalize()}"
                     ).set_thumbnail(url=(
                         "https://cdn.discordapp.com/avatars/940719011405123625"
                         "/a39422f00e782226b50c8bcb2d80dadf.webp?size=80s"
                     ))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
