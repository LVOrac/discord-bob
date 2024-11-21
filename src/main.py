"""
make a command to request the score in deanza
todo:
    adddir [dir]
    rmdir [dir]
    chdir [section]
    add [todo]
    rm  [todo]

play:
    music [music name]
"""

import os

folder_path: str = os.path.join("users")
os.chdir(folder_path)

from bot_setup import client, TOKEN, tree
from discord import Message
from discord.app_commands import Command

from todo_commands import TodoCommands
from user import init, delete

tree.add_command(TodoCommands())
tree.add_command(Command(name="init", description="initialize user", callback=init))
tree.add_command(Command(name="del", description="delete user", callback=delete))

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
