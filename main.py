import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message

load_dotenv()

TOKEN = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True

client: Client = Client(intents=intents)

def get_response(user_input: str) -> str:
    os.system(f"python -c \"{user_input}\" > .output 2>&1")
    with open('.output', 'r') as f:
        result = f.read()
    return result

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        return
    try:
        response: str = get_response(user_message)
        await message.author.send(response)
    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f"{client.user} is ready")


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    username: str = str(message.author)
    user_message: str = str(message.content)
    channel: str = str(message.channel)
    print(f"{username} {channel}: {user_message}")
    await send_message(message, user_message)

def main() -> None:
    client.run(token=TOKEN)

if __name__ == "__main__":
    main()
