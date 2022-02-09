from datetime import datetime
from disnake.ext import commands
from utils import time_converter
from constants import Colours
from models.buttons.lobbygate import LobbyGate
from models.buttons.confirm import Confirm
from disnake import TextChannel, Member, Embed, PermissionOverwrite, VoiceChannel


class GameLobby:
    """Class representing a game lobby"""

    def __init__(
        self,
        bot: commands.Bot,
        lobby_starter: Member,
        players_required: int,
        description: str,
        channel: TextChannel,
        lobby_id: int
    ):
        self.bot: commands.Bot = bot
        self.players: list[Member] = [lobby_starter]
        self.players_required: int = players_required
        self.description: int = description
        self.channel: TextChannel = channel
        self.created_at: datetime = datetime.utcnow()
        self.started: bool = False
        self.text_channel: TextChannel = None
        self.voice_channel: VoiceChannel = None
        self.lobby_id: int = lobby_id

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
        await self.channel.send(
            f"__New player has joined!__\n{member} just joined the lobby,"
            f" {len(self.players)} players in the lobby now."
        )

    async def left_alert(self, member: Member):
        await self.channel.send(
            f"__A player has left the lobby__\n{member} just left the lobby,"
            f" {len(self.players)} players in the lobby now."
        )

    async def start(self) -> None:
        overwrites = {
            self.channel.guild.default_role: PermissionOverwrite(view_channel=False),
        }

        text_channel = await self.channel.guild.create_text_channel(
            name="lobby_" + str(self.lobby_id),
            overwrites=overwrites)
        self.text_channel = text_channel

        voice_channel = await self.channel.guild.create_voice_channel(
            name="lobby_" + str(self.lobby_id),
            overwrites=overwrites)
        self.voice_channel = voice_channel

        embed: Embed = Embed(
            title="The lobby is filled!",
            description=self.description,
            color=Colours.SUCCESS.value
        )
        await self.message.edit(embed=embed, view=None)

        mentions = " ".join([player.mention for player in self.players])

        await self.channel.send(
            "The lobby is filled! Head over to "
            f"`{text_channel}` text and voice channels. {mentions}"
        )
        self.started = True

    async def close(self) -> None:
        embed: Embed = Embed(
            title="Lobby has been closed",
            description=self.description,
            color=Colours.INFO.value
        ).add_field(
            name="Closed by",
            value=self.players[0]  # The starter is the first player
        )
        view = Confirm()
        if self.started:
            message = await self.channel.send(
                "The lobby has been started, are you sure you want to close it?",
                view=view
            )
            await view.wait()
            if view.value:
                await self.message.edit(embed=embed, view=None)
                await self.text_channel.delete()
                await self.voice_channel.delete()
                await message.delete()
        else:
            await self.message.edit(embed=embed, view=None)


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

    @commands.command()
    async def lobby(
        self,
        ctx: commands.Context,
        channel: TextChannel = None,
        *,
        metadata: str = None,
    ):

        if channel is None or metadata is None:
            return await ctx.send(
                "You need to define the channel and metadata both.\n"
                "Optionally change the player amount and timeout "
                "using `--players` and `--timeout` flags. Example:"
                "```!lobby #bot-commands Warzone duos --players 2 --timeout 1h```"
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
        players_required: int = 4
        description: str = metadata
        conversions = {"s": "seconds",
                       "m": "minutes", "h": "hours", "d": "days"}
        readable_timeout: str = timeout[:-1] + " " + conversions[timeout[-1]]

        if "--timeout" in metadata:
            timeout: str = metadata.split(
                "--timeout ")[1].split("--players")[0].replace(" ", "")

            readable_timeout: str = timeout[:-1] + \
                " " + conversions[timeout[-1]]
            description: str = metadata[:metadata.find("--timeout")]

        if "--players" in metadata:
            players_required: str = metadata.split(
                "--players ")[1].split("--timeout")[0].replace(" ", "")
            description: str = description[:metadata.find("--players")]

            if not players_required.isdigit():
                return await ctx.send("Players must be an integer")
            if int(players_required) < 2:
                return await ctx.send("A lobby requires two or more players")

            players_required: int = int(players_required)
        try:
            timeout: int = time_converter(timeout)
        except ValueError as e:
            return await ctx.send(e)

        lobby = GameLobby(
            self.bot,
            ctx.author,
            players_required,
            description,
            channel,
            len(self.lobbies) + 1
        )
        self.lobbies.append(lobby)

        embed = Embed(
            title=(
                "A new lobby has been started!\n"
                f"{lobby.players_required} players required."
            ),
            description=description,
            color=Colours.SUCCESS.value
        ).add_field(
            name="Players in lobby",
            value=ctx.author,
            inline=False
        ).add_field(
            name="Closing in",
            value=readable_timeout,
            inline=False
        ).add_field(
            name="Lobby ID",
            value=lobby.lobby_id,
            inline=False
        ).set_footer(
            text="Waiting for players to join..."
        ).set_author(
            name=ctx.author, icon_url=ctx.author.avatar.url if ctx.author.avatar else "https://discord.com/assets/c09a43a372ba81e3018c3151d4ed4773.png"
        )
        view = LobbyGate(ctx, embed, lobby, self.lobbies, timeout)

        message = await channel.send(embed=embed, view=view)
        view.message = message
        lobby.message = message

    @commands.command()
    async def close(self, ctx: commands.Context):
        if self.check_playing(ctx.author):
            match = self.get_lobby(ctx.author)
            await match.close()
            self.lobbies.remove(match)
        else:
            await ctx.send("You have not started any lobby.")


def setup(bot):
    bot.add_cog(Lobby(bot))
