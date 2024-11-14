import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message, Interaction, app_commands
# from appdirs import user_data_dir

load_dotenv()

TOKEN = str(os.getenv("DISCORD_TOKEN"))

intents: Intents = Intents.default()
intents.message_content = True

folder_path = os.path.join("users")

class Style:
    Italics         = 0b1
    Bold            = 0b10
    Underline       = 0b100
    Strikethrough   = 0b1000
    Spoilers        = 0b10000
    BulletedList    = 0b100000

# Reference: https://discord.com/blog/make-your-discord-messages-bold-italic-underlined-and-more
def format(text, header = None, style: int = 0) -> str:
    if style & 0b100000 == Style.BulletedList:
        text = f"- {text}"
    if header:
        text = f"{header} {text}"
    if style & 0b001 == Style.Italics:
        text = f"_{text}_"
    if style & 0b010 == Style.Bold:
        text = f"**{text}**"
    if style & 0b100 == Style.Underline:
        text = f"__{text}__"
    if style & 0b1000 == Style.Strikethrough:
        text = f"~~{text}~~"
    if style & 0b10000 == Style.Spoilers:
        text = f"||{text}||"
    return text

client: Client = Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="fontstyles", description="this will show some font styles")
async def fontstyles(interaction: Interaction) -> None:
    out = ""
    for style in range(0b111111):
        out += format("This is some text\u2665", style=style) + '\n'
    await interaction.response.send_message(out)

@tree.command(name="init", description="this will generate an init folder")
async def init_todo(interaction: Interaction) -> None:
    user_data_path = os.path.join("users", str(interaction.user.id))
    os.makedirs(user_data_path, exist_ok=True)
    await interaction.response.send_message(str(interaction.user.id) + ": init complete!")

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
    await tree.sync(guild=None) # you may need to wait a bit for syncing the commands
    os.makedirs(folder_path, exist_ok=True)
    # print(str(client.user.id))
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
