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
        platform: str,
        region: str,
        no_mic: bool,
        info: str,
        channel: TextChannel,
        game: str
    ):
        self.bot: commands.Bot = bot
        self.players: list[Member] = [lobby_starter]
        self.players_required: int = players_required
        self.description: int = description
        self.region: str = region
        self.platform: str = platform
        self.no_mic: bool = no_mic
        self.info: str = info
        self.channel: TextChannel = channel
        self.game: str = game

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

    async def create_channels(self) -> None:
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

        if not self.no_mic:
            voice_channel: TextChannel = await guild.create_voice_channel(
                name=self.players[0].name + "'s Lobby",
                overwrites=overwrites,
                category=guild.get_channel(LOBBY_CATEGORY_ID)
            )
            self.voice_channel = voice_channel

    async def drop_game_ids(self) -> None:
        db = self.bot.mongo_client["LinkGame"]
        users = [db[str(player.id)][self.platform] for player in self.players]
        desc = ""
        for player in self.players:
            data = await users[self.players.index(player)].find_one({"game": self.game.lower()})
            if data:
                desc += f"{player}: {data['id']}\n"
            else:
                desc += f"{player}: *Game not linked*\n"
        embed: Embed = Embed(title="Player IDs", description=desc, color=Colours.INFO.value
                             )
        message = await self.text_channel.send(embed=embed)
        self.id_message = message

    async def update_id_embed(self) -> None:
        db = self.bot.mongo_client["LinkGame"]
        users = [db[str(player.id)][self.platform] for player in self.players]
        desc = ""
        for player in self.players:
            data = await users[self.players.index(player)].find_one({"game": self.game.lower()})
            if data:
                desc += f"{player}: {data['id']}\n"
            else:
                desc += f"{player}: *Game not linked*\n"
        embed: Embed = Embed(title="Player IDs", description=desc, color=Colours.INFO.value
                             )
        message = await self.id_message.edit(embed=embed)

    async def update_embed(self) -> None:
        self.embed.clear_fields()
        self.embed.add_field(
            name="Slots",
            value=f"{len(self.players)}/{self.players_required}",
            inline=False
        ).add_field(
            name="Players in lobby",
            value="\n".join(
                [str(player) for player in self.players]
            ),
            inline=False
        ).add_field(
            name="Region",
            value=self.region,
            inline=False
        ).add_field(
            name="Closing in",
            value="30 minutes",
            inline=False
        )
        await self.message.edit(embed=self.embed)

    async def start(self) -> None:
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
            f"`{self.text_channel.name}` text and voice channels. {mentions}"
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
    async def lobby(self, ctx: commands.Context) -> None:
        await ctx.send("Invalid or missing parameters, use the following format:```!lobby create <region> <platform> <mic-req> <description>```")

    @commands.command()
    async def close(self, ctx: commands.Context) -> None:
        await ctx.send("Perhaps, you meant `!lobby close`?")

    @lobby.command()
    async def create(
        self,
        ctx: commands.Context,
        region: str = None,
        platform: str = None,
        no_mic: str = None,
        player_amount: str = None,
        *,
        description: str = "Looking for players",
    ) -> None:

        players_required: int = 4
        info: str = None
        channel = ctx.channel
        category_name: str = channel.category.name.lower()
        game_list = [i for i in SUPPORTED_GAMES if i in category_name]
        if game_list:
            game: str = game_list[0].capitalize()
            mode: str = channel.name.lower()
            info: str = f"{game} {mode}"
            players_required: int = game_mode_to_players.get(mode, 4)

        else:
            return await ctx.send("Unsupported game channel")
        print(player_amount)
        if game.lower() == "warzone" or game.lower() == "halo":
            if mode.lower() in ["rebirth", "plunder", "crossplay"] and not player_amount or not player_amount.isdigit():
                return await ctx.send("You need to specify player amount after mic argument for this game mode")

        help_message = "Invalid or missing parameters, use the following format:```!lobby create <region> <platform> <mic-req> <description>```"
        if not region or not platform or not no_mic:
            return await ctx.send(help_message)

        platforms_options = ["acti", "psn", "xbox", "battle", "origin", "riot", "steam"]
        if platform not in platforms_options:
            return await ctx.send("You need to add a platform from the following - acti, psn, xbox, battle, origin, riot, epic and steam")

        if no_mic.lower() not in ["no-mic", "mic-req"]:
            return await ctx.send("You need to specifiy if mic is not required or not by adding 'no-mic' or 'mic-req'")

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
                name="Region",
                value=region,
                inline=False
            ).add_field(
                name="Platform",
                value=platform.upper(),
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
        players_required: int = game_mode_to_players.get(
            channel.name.lower(), 4)
        try:
            timeout: int = time_converter(timeout)
        except ValueError as e:
            return await ctx.send(e)

        lobby: GameLobby = GameLobby(
            self.bot,
            ctx.author,
            int(player_amount) or players_required,
            description,
            platform,
            region,
            True if no_mic == "no-mic" else False,
            info,
            channel,
            game
        )
        self.lobbies.append(lobby)
        await lobby.create_channels()
        await lobby.drop_game_ids()
        embed: Embed = Embed(
            title=f"A NEW LOBBY HAS BEEN CREATED!",
            description=description,
            color=Colours.ERROR.value
        ).add_field(
            name="Type",
            value=info,
        ).add_field(
            name="Slots",
            value=f"{len(lobby.players)}/{player_amount or players_required}",
        ).add_field(
            name="Players in lobby",
            value=ctx.author,
        ).add_field(
            name="Region",
            value=region,
        ).add_field(
            name="Platform",
            value=platform.upper(),
        ).add_field(
            name="Mic required",
            value="No" if no_mic else "Yes",
        ).add_field(
            name="Closing in",
            value="30 minutes",
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
        lobby.embed = embed

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
                    await lobby.close()
                    self.lobbies.remove(lobby)
                    await lobby.text_channel.delete()
                    if not lobby.no_mic:
                        await lobby.voice_channel.delete()
                    await ctx.send("The lobby has been closed.")
            else:
                await lobby.close()
                self.lobbies.remove(lobby)
                await lobby.text_channel.delete()
                if lobby.no_mic:
                    await lobby.voice_channel.delete()
                await ctx.send("The lobby has been closed.")
        else:
            await ctx.send("You have not started any lobby.")

    @lobby.command()
    async def leave(self, ctx: commands.Context) -> None:
        if not self.check_playing(ctx.author):
            return await ctx.send("You are not in any lobby")
        lobby = self.get_lobby(ctx.author)
        if ctx.author == lobby.players[0]:
            return await ctx.send("You cannot leave the lobby since you are the lobby leader.")
        lobby.remove_player(ctx.author)
        await lobby.update_embed()
        await ctx.reply("Successfully left the lobby")


def setup(bot):
    bot.add_cog(Lobby(bot))
