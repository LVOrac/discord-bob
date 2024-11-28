import os
import shutil
import json
from discord import Interaction

def load_json(id: int, name: str):
    path: str = os.path.join(str(id), name)
    if not os.path.exists(path):
        return None

    with open(path, 'r') as f:
        return json.load(f)

def initialized_user(interaction: Interaction) -> str | None:
    user_folder = str(interaction.user.id)
    if os.path.exists(user_folder):
        return user_folder
    return None

def init_user(interaction: Interaction) -> None:
    user_folder = str(interaction.user.id)
    os.makedirs(user_folder, exist_ok=True)

async def init(interaction: Interaction) -> None:
    path = initialized_user(interaction)
    if path == None:
        init_user(interaction)
        await interaction.response.send_message(str(interaction.user.id) + ": init complete!")
        return
    await interaction.response.send_message(str(interaction.user.id) + ": already exists!")

async def delete(interaction: Interaction) -> None:
    path = initialized_user(interaction)
    if path == None:
        await interaction.response.send_message(str(interaction.user.id) + ": user do not exist!")
        return
    shutil.rmtree(path)
    await interaction.response.send_message(str(interaction.user.id) + ": delete complete!")
