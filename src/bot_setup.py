import os 
from dotenv import load_dotenv
from discord import Intents, Client

load_dotenv()
TOKEN: str = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
