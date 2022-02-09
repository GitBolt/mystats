import disnake


class Confirm(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value: bool = None

    @disnake.ui.button(label="Confirm", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("The lobby has been closed.")
        self.value = True
        self.stop()

    @disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.red)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_message("Aborted lobby closing process.")
        self.value = False
        self.stop()