import discord

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.confirmed = None

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.confirmed = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.confirmed = False
        self.stop()

class DropDownMenu(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed()
        await interaction.response.edit_message(embed=embed)

class ProfileView(discord.ui.View):
    def __init__(self, user: discord.Member, userTrades: list):
        super().__init__()
        self.user = user
        self.pageNum = 1
        self.pages = userTrades % 10
        self.userTrades = userTrades

    # def __createProfileEmbed(self):
    #     await self.
        
class TradesView(discord.ui.View):
    def __init__(self, user: discord.Member, userTrades: list):
        super().__init__()
        self.add_item(DropDownMenu(
            options=[
                discord.SelectOption(description="Trades", value="trades", default=True),
                discord.SelectOption(description="Profile", value="profile")
                ]
        ))
        self.user = user
        self.pageNum = 1
        self.pages = userTrades % 10
        self.userTrades = userTrades

    def __createTradesPageEmbed(self):
        self.pageNum = self.pageNum % len(self.pages)