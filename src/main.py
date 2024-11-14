import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction, app_commands
import text_style as ts
# from appdirs import user_data_dir

load_dotenv()

TOKEN = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True

folder_path = os.path.join("users")
client: Client = Client(intents=intents)

tree = app_commands.CommandTree(client)

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
    await tree.sync(guild=None) # you need to restart discord if there is a new command which needs to be updated.
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