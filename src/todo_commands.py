from discord import app_commands
from discord import Interaction

class TodoCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="todo", description="todo commands")

    @app_commands.command(name="addlist", description="add a new todo-list")
    @app_commands.describe(name="list name")
    async def addlist(self, interaction: Interaction, name: str):
        await interaction.response.send_message("add new list - " + name)

    @app_commands.command(name="add", description="add task")
    @app_commands.describe(name="task name")
    async def add(self, interaction: Interaction, name: str):
        await interaction.response.send_message("add a new task - " + name)
