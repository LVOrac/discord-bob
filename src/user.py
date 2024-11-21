import os
from discord import Interaction

def initialized_user(interaction: Interaction) -> str | None:
    user_folder = str(interaction.user.id)
    if os.path.exists(user_folder) and os.path.isdir(user_folder):
        return user_folder
    return None

def init_user(interaction: Interaction) -> None:
    user_folder = str(interaction.user.id)
    os.makedirs(user_folder, exist_ok=True)

