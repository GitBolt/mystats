import disnake
from disnake.ext.commands import Context


class LobbyGate(disnake.ui.View):
    def __init__(self, ctx: Context, timeout: int):
        super().__init__(timeout=timeout)
        self.value: bool = None
        self.ctx: Context = ctx

    async def on_timeout(self):
        await self.message.edit(content="Match", embed=None, view=None)

    @disnake.ui.button(label="Join", style=disnake.ButtonStyle.green)
    async def confirm(
                    self,
                    button: disnake.ui.Button,
                    interaction: disnake.MessageInteraction
                      ):
        await interaction.response.send_message(
            "Successfully joined the lobby",
            ephemeral=True
        )
        self.value = True

    @disnake.ui.button(label="Leave", style=disnake.ButtonStyle.red)
    async def cancel(
                    self,
                    button: disnake.ui.Button,
                    interaction: disnake.MessageInteraction
                     ):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
