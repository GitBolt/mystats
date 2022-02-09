import disnake
from disnake.ext.commands import Context
from disnake import Member, Embed, MessageInteraction
from constants import Colours


class LobbyGate(disnake.ui.View):
    def __init__(self, ctx: Context, embed: Embed, lobby, lobbieslist, timeout: int):
        super().__init__(timeout=timeout)
        self.ctx: Context = ctx
        self.embed = embed
        self.lobby = lobby
        self.lobbieslist = lobbieslist

    async def on_timeout(self):
        self.embed.title = "Lobby timeout"
        self.embed.clear_fields()
        self.embed.set_footer(text="")
        self.embed.add_field(
            name="Started by",
            value=self.ctx.author,
            inline=False
        )
        self.embed.add_field(
            name="Required players",
            value=self.lobby.players_required,
            inline=False
        )
        self.embed.color = Colours.WARNING.value
        await self.message.edit(embed=self.embed, view=None)
        self.lobbieslist.remove(self.lobby)

    @disnake.ui.button(label="Join", style=disnake.ButtonStyle.green)
    async def join(
        self,
        button: disnake.ui.Button,
        interaction: MessageInteraction
    ):
        if interaction.author in self.lobby.players:
            await interaction.response.send_message(
                "You are already in the lobby",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Successfully joined the lobby",
                ephemeral=True
            )
            self.lobby.add_player(interaction.author)

            self.embed.clear_fields()
            self.embed.add_field(name="Players in lobby", value="\n".join(
                [str(player) for player in self.lobby.players]))
            await self.message.edit(embed=self.embed)
            await self.lobby.join_alert(interaction.author)

            if len(self.lobby.players) == self.lobby.players_required:
                await self.lobby.start()

    @disnake.ui.button(label="Leave", style=disnake.ButtonStyle.red)
    async def leave(
        self,
        button: disnake.ui.Button,
        interaction: MessageInteraction
    ):
        if interaction.author == self.ctx.author:
            await interaction.response.send_message(
                ("You cannot leave the lobby since you started it. "
                 "Type `!close` if you want to close this lobby."),
                ephemeral=True
            )

        elif interaction.author not in self.lobby.players:
            await interaction.response.send_message(
                "You are not in the lobby",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You have left the lobby",
                ephemeral=True
            )
            self.lobby.remove_player(interaction.author)
            self.embed.clear_fields()
            self.embed.add_field(name="Players in lobby", value="\n".join(
                [str(player) for player in self.lobby.players]))
            await self.message.edit(embed=self.embed)
            await self.lobby.join_alert(interaction.author)
