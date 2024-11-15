import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction
import discord
from discord.ui import Select, View
import discord.app_commands as ac
import text_style as ts

"""
todo:
    adddir [dir]
    rmdir [dir]
    chdir [section]
    add [todo]
    rm  [todo]

play:
    music [music name]
"""

load_dotenv()
TOKEN: str = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

folder_path: str = os.path.join("users")

tree: ac.CommandTree = ac.CommandTree(client)

class TodoList(ac.Group):
    def __init__(self):
        super().__init__(name="todo", description="todo commands")

    @ac.command(name="addlist", description="add a new todo-list")
    @ac.describe(todo_list="list name")
    async def addlist(self, interaction: Interaction, todo_list: str):
        await interaction.response.send_message("add new list - " + todo_list)

    @ac.command(name="add", description="add task")
    @ac.describe(task="task name")
    async def add(self, interaction: Interaction, task: str):
        await interaction.response.send_message("add a new task - " + task)

tree.add_command(TodoList())

@tree.command(name="fontstyles", description="this will show some font styles")
async def fontstyles(interaction: Interaction) -> None:
    out = ""
    for style in range(0b111111):
        out += ts.format("This is some text\u2665", style=style) + '\n'
    await interaction.response.send_message(out)

@tree.command(name="init", description="this will generate an init folder")
async def init_todo(interaction: Interaction) -> None:
    user_data_path = os.path.join("users", str(interaction.user.id))
    if os.path.exists(user_data_path):
        await interaction.response.send_message(str(interaction.user.id) + ": already exists!")
        return
        
    os.makedirs(user_data_path, exist_ok=True)
    await interaction.response.send_message(str(interaction.user.id) + ": init complete!")

@client.event
async def on_ready() -> None:
    await tree.sync(guild=None) # you may need to restart discord if there is a new command which needs to be updated.
    os.makedirs(folder_path, exist_ok=True)
    print(f"{client.user} is ready")

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    username: str = str(message.author)
    user_message: str = str(message.content)
    channel: str = str(message.channel)
    print(f"{username} {channel}: {user_message}")

def main() -> None:
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()
