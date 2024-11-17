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

import os

folder_path: str = os.path.join("users")
os.chdir(folder_path)

from bot_setup import client, TOKEN
from discord import Message, Interaction
import discord.app_commands as ac
import text_style as ts

from todo_commands import TodoCommands

tree: ac.CommandTree = ac.CommandTree(client)
tree.add_command(TodoCommands())

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
