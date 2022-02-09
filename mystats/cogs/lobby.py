from datetime import datetime
from disnake import TextChannel, Member, Embed
from disnake.ext import commands
from utils import time_converter
from constants import Colours
from models.buttons import LobbyGate


class GameLobby:
    """Class representing a game lobby"""

    def __init__(
        self,
        bot: commands.Bot,
        lobby_starter: Member,
        players_required: int,
        description: str
    ):
        self.bot: commands.Bot = bot
        self.players: list[Member] = [lobby_starter]
        self.players_required: int = players_required
        self.description: int = description
        self.created_at: datetime = datetime.utcnow()

    def add_player(self, player: Member) -> None:
        self.players.append(player)

    def remove_player(self, player: Member) -> None:
        self.players.remove(player)

    def time_elapsed(self):
        time = datetime.utcnow() - self.created_at
        if time.total_seconds() < 60:
            return f"{round(time.total_seconds(), 1)} seconds"
        else:
            return f"{round(time.total_seconds() / 60, 1)} minutes"

    async def join_alert(self, member: Member):
        for player in self.players:
            await player.send(
                f"__New player has joined!__\n{member} just joined the lobby,"
                f" {len(self.players)} players in the lobby now."
            )

    async def start(self):
        count = 5
        embed = Embed(
            title="All players joined!",
            description=f"Match starting in {count}...",
            color=Colours.DEFAULT,
        ).add_field(
            name="Started", value=f"{self.time_elapsed()} ago", inline=False
        ).add_field(
            name="Players", value="\n".join(
                [str(player) for player in self.players]
            ), inline=False
        )
        for player in self.players:
            await player.send(embed=embed)


class Lobby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lobbies: list[GameLobby] = []

    def check_playing(self, player: Member):
        return any(player in lobby.players for lobby in self.lobbies)

    def get_lobby(self, player: Member):
        for lobby in self.lobbies:
            if player in lobby.players:
                return lobby

    @commands.command(name="lobby")
    async def lobby(
        self,
        ctx: commands.Context,
        channel: TextChannel = None,
        *,
        metadata: str = None,
    ):
        if channel is None:
            return await ctx.send(
                "You need to define the channel, "
                "either by mentioning it or using it's ID."
            )
        if metadata is None:
            return await ctx.send(
                "You need to define the description too! "
                "Optionally change player amount and timeout "
                "using `--players` and `--timeout` flags"
            )

        if self.check_playing(ctx.author):
            match = self.get_lobby(ctx.author)

            embed = Embed(
                title="Lobby info",
                description=(
                    "The lobby currently has "
                    f"**{len(match.players)}** players"
                ),
                color=Colours.WARNING.value
            ).add_field(
                name="Started",
                value=match.time_elapsed()+" ago",
                inline=False
            ).add_field(
                name="Players required",
                value=match.players_required,
                inline=False
            )

            return await ctx.send(
                content=f"You are already in a lobby {ctx.author.mention}",
                embed=embed
            )

        timeout: str = "30m"
        player_amount: int = 4
        description: str = None

        if "--timeout" in metadata:
            timeout: str = metadata.split("--timeout ")[1]
            description: str = metadata[:metadata.find("--timeout")]

        if "--players" in metadata:
            players: str = metadata.split("--players ")[1]
            description: str = description[:metadata.find("--timeout")]
            if not players.isdigit():
                return await ctx.send("Players must be an integer")

        lobby = GameLobby(
            self.bot,
            ctx.author,
            player_amount,
            description
        )
        self.lobbies.append(lobby)

        embed = Embed(
            title="A new lobby has been started!",
            color=Colours.SUCCESS.value
        ).add_field(
            name="Players required",
            value=lobby.players_required,
            inline=False
        ).set_footer(
            text="Waiting for players to join..."
        ).set_author(
            name=ctx.author, icon_url=ctx.author.avatar.url
        )

        view = LobbyGate(ctx, time_converter(timeout))
        view.message = await channel.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Lobby(bot))
