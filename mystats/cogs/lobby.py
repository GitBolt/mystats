from datetime import datetime
from statistics import mode
from disnake.ext import commands
from utils import time_converter, game_mode_to_players
from constants import Colours
from models.buttons.lobbygate import LobbyGate
from models.buttons.confirm import Confirm
from disnake import (
    TextChannel,
    Member,
    Embed,
    PermissionOverwrite,
    VoiceChannel,
    Role,
    Guild,
    Message
)


SUPPORTED_GAMES: tuple[str, str, str, str] = (
    "warzone",
    "fortnite",
    "apex",
    "halo"
)
LOBBY_CATEGORY_ID = 941376025936429108

class GameLobby:
    """Class representing a game lobby"""

    def __init__(
        self,
        bot: commands.Bot,
        lobby_starter: Member,
        players_required: int,
        description: str,
        info: str,
        channel: TextChannel,
    ):
        self.bot: commands.Bot = bot
        self.players: list[Member] = [lobby_starter]
        self.players_required: int = players_required
        self.description: int = description
        self.info: str = info
        self.channel: TextChannel = channel

        self.created_at: datetime = datetime.utcnow()
        self.started: bool = False
        self.text_channel: TextChannel = None
        self.voice_channel: VoiceChannel = None

    def add_player(self, player: Member) -> None:
        self.players.append(player)

    def remove_player(self, player: Member) -> None:
        self.players.remove(player)

    def time_elapsed(self):
        time: datetime = datetime.utcnow() - self.created_at
        if time.total_seconds() < 60:
            return f"{round(time.total_seconds(), 1)} seconds"
        else:
            return f"{round(time.total_seconds() / 60, 1)} minutes"

    async def join_alert(self, member: Member) -> None:
        await self.channel.send(
            f"__New player has joined!__\n{member} just joined the lobby,"
            f" {len(self.players)} players in the lobby now."
        )

    async def leave_alert(self, member: Member) -> None:
        await self.channel.send(
            f"__A player has left the lobby__\n{member} just left the lobby,"
            f" {len(self.players)} players in the lobby now."
        )

    async def start(self) -> None:
        guild: Guild = self.channel.guild
        overwrites: dict[Role, PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(view_channel=False),
        }

        text_channel: TextChannel = await guild.create_text_channel(
            name=self.players[0].name + "'s Lobby",
            overwrites=overwrites,
            category=guild.get_channel(LOBBY_CATEGORY_ID)
        )
        self.text_channel = text_channel

        voice_channel: TextChannel = await guild.create_voice_channel(
            name=self.players[0].name + "'s Lobby",
            overwrites=overwrites,
            category=guild.get_channel(LOBBY_CATEGORY_ID)
        )
        self.voice_channel = voice_channel

        embed: Embed = Embed(
            title=f"The lobby is filled!\n{self.info}",
            description=self.description,
            color=Colours.SUCCESS.value
        ).add_field(
            name="Slots",
            value=f"{len(self.players)}/{self.players_required}",
            inline=False
        ).add_field(
            name="Players in lobby",
            value="\n".join(
                [str(player) for player in self.players]
            ),
            inline=False
        )
        await self.message.edit(embed=embed, view=None)

        mentions = " ".join([player.mention for player in self.players])
        await self.channel.send(
            "The lobby is filled! Head over to "
            f"`{voice_channel}` text and voice channels. {mentions}"
        )
        self.started = True

    async def close(self) -> None:
        embed: Embed = Embed(
            title="Lobby has been closed",
            description=self.description,
            color=Colours.WARNING.value
        ).add_field(
            name="Closed by",
            value=self.players[0]  # The starter is the first player
        )

        await self.message.edit(embed=embed, view=None)


class Lobby(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.lobbies: list[GameLobby] = []

    def check_playing(self, player: Member) -> None:
        return any(player in lobby.players for lobby in self.lobbies)

    def get_lobby(self, player: Member) -> None:
        for lobby in self.lobbies:
            if player in lobby.players:
                return lobby

    @commands.group(pass_context=True, invoke_without_command=True)
    async def lobby(self, ctx):
        await ctx.send("Perhaps, you meant `!lobby create`?")

    @lobby.command()
    async def create(
        self,
        ctx: commands.Context,
        channel: TextChannel = None,
        *,
        description: str = "Looking for players",
    ) -> None:

        players_required: int = 4
        info: str = None
        if [i for i in SUPPORTED_GAMES if i in ctx.channel.category.name.lower()]:
            print("Yes")
            channel: TextChannel = ctx.channel

            game: str = [i for i in SUPPORTED_GAMES if i in ctx.channel.category.name.lower()][0].capitalize()
            mode: str = channel.name.lower()
            info: str = f"{game} {mode}"

            players_required: int = game_mode_to_players[mode]

        if channel is None:
            return await ctx.send(
                "Since you are not in a game channel, you would need to "
                "define the channel in the command too, optionally add a "
                "description. Example:```!lobby create #duos Looking for a quick match```"
            )

        if self.check_playing(ctx.author):
            lobby: GameLobby = self.get_lobby(ctx.author)

            embed: Embed = Embed(
                title=lobby.info,
                description=lobby.description,
                color=Colours.WARNING.value
            ).add_field(
                name="Started",
                value=lobby.time_elapsed()+" ago",
                inline=False
            ).add_field(
                name="Players in lobby",
                value=" ".join([str(x) for x in lobby.players]),
                inline=False
            )

            return await ctx.send(
                content=f"You are already in a lobby {ctx.author.mention}",
                embed=embed
            )

        timeout: str = "30m"
        players_required: int = game_mode_to_players[channel.name.lower()]
        try:
            timeout: int = time_converter(timeout)
        except ValueError as e:
            return await ctx.send(e)

        lobby: GameLobby = GameLobby(
            self.bot,
            ctx.author,
            players_required,
            description,
            info,
            channel,
        )
        self.lobbies.append(lobby)

        embed: Embed = Embed(
            title=f"A new lobby has been started!\n{info}",
            description=description,
            color=Colours.SUCCESS.value
        ).add_field(
            name="Slots",
            value=f"{len(lobby.players)}/{players_required}",
            inline=False
        ).add_field(
            name="Players in lobby",
            value=ctx.author,
            inline=False
        ).add_field(
            name="Closing in",
            value="30 minutes",
            inline=False
        ).set_footer(
            text="Waiting for players to join..."
        ).set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else
            "https://discord.com/assets/c09a43a372ba81e3018c3151d4ed4773.png"
        )
        view: LobbyGate = LobbyGate(ctx, embed, lobby, self.lobbies, timeout)

        message: Message = await channel.send(embed=embed, view=view)
        view.message = message
        lobby.message = message

    @lobby.command()
    async def close(self, ctx: commands.Context) -> None:
        if self.check_playing(ctx.author):
            lobby: GameLobby = self.get_lobby(ctx.author)
            if lobby.started:
                view: Confirm = Confirm()
                message: Message = await lobby.channel.send((
                    "The lobby has been started, "
                    "are you sure you want to close it?"
                ),
                    view=view
                )
                await view.wait()
                await message.edit(view=None)
                if view.value:
                    await lobby.text_channel.delete()
                    await lobby.voice_channel.delete()
                    await lobby.close()
                    self.lobbies.remove(lobby)
            else:
                await lobby.close()
                self.lobbies.remove(lobby)
        else:
            await ctx.send("You have not started any lobby.")


def setup(bot):
    bot.add_cog(Lobby(bot))
