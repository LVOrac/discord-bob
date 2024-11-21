import os 
from dotenv import load_dotenv
from discord import Intents, Client
import discord.app_commands as ac

load_dotenv()
TOKEN: str = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

tree: ac.CommandTree = ac.CommandTree(client)
