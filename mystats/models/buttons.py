import disnake
from disnake.ext.commands import Context
from disnake import Member, Embed, MessageInteraction
from constants import Colours


class LobbyGate(disnake.ui.View):
    def __init__(self, ctx: Context, embed: Embed, timeout: int):
        super().__init__(timeout=timeout)
        self.ctx: Context = ctx
        self.embed = embed

    async def update_embed(self, member: Member, add=True):
        if add:
            self.embed.fields[0].value += f"\n{member}"
        else:
            self.embed.fields[0] = self.embed.fields[0].value.replace(
                f"\n{member}", ""
            )
        await self.message.edit(embed=self.embed)

    async def on_timeout(self):
        self.embed.title = "Lobby timeout"
        self.embed.clear_fields()
        self.embed.set_footer(text="")
        self.embed.color = Colours.INFO.value
        await self.message.edit(embed=self.embed, view=None)

    @disnake.ui.button(label="Join", style=disnake.ButtonStyle.green)
    async def join(
        self,
        button: disnake.ui.Button,
        interaction: MessageInteraction
    ):
        await interaction.response.send_message(
            "Successfully joined the lobby",
            ephemeral=True
        )
        await self.update_embed(interaction.author)

    @disnake.ui.button(label="Leave", style=disnake.ButtonStyle.red)
    async def leave(
        self,
        button: disnake.ui.Button,
        interaction: MessageInteraction
    ):
        await interaction.response.send_message("Left the lobby", ephemeral=True)
        await self.update_embed(interaction.author, add=False)
