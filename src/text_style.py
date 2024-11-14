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

