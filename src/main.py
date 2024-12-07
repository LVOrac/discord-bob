import os

folder_path: str = os.path.join("users")
os.chdir(folder_path)

import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.app_commands import Command, CommandTree

load_dotenv()
TOKEN: str = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

tree: CommandTree = CommandTree(client)

from todo_commands import TodoCommands
from chess_commands import ChessCommands
from user import init, delete, help
from weather_commands import WeatherCommands

tree.add_command(TodoCommands())
tree.add_command(ChessCommands())
tree.add_command(WeatherCommands())
tree.add_command(Command(name="init", description="initialize user", callback=init))
tree.add_command(Command(name="del", description="delete user", callback=delete))
tree.add_command(Command(name="help", description="help", callback=help))

@client.event
async def on_ready() -> None:
    await tree.sync(guild=None) # you may need to restart discord if there is a new command which needs to be updated.
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
