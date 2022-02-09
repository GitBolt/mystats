import disnake


class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @disnake.ui.button(label="Join", style=disnake.ButtonStyle.green)
    async def confirm(self,
                      button: disnake.ui.Button,
                      interaction: disnake.MessageInteraction):
        await interaction.response.send_message(
            "Successfully joined the lobby",
            ephemeral=True
        )
        self.value = True
        self.stop()

    @disnake.ui.button(label="Leave", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()
