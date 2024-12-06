import os
import json
from discord import Interaction, File
from typing import Optional
from discord.app_commands import Group, Choice, describe, command, choices
from text_style import format, Style
import requests
from user import user_initialized

import chess
from chess.engine import SimpleEngine, Limit
from chess import svg
from cairosvg import svg2png

from dotenv import load_dotenv

load_dotenv()
STOCKFISH: str = str(os.getenv("STOCKFISH"))

def save_stockfish_config(interaction: Interaction, level: int, depth: int, response_time: float) -> None:
    path: str = os.path.join(str(interaction.user.id), "stockfish_config.json")
    with open(path, 'w') as f:
        f.write(f"[{level},{depth},{response_time}]")

def load_stockfish_config(interaction: Interaction):
    path: str = os.path.join(str(interaction.user.id), "stockfish_config.json")
    with open(path, 'r') as f:
        return json.load(f)

def board_exist(interaction: Interaction) -> bool:
    board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
    return os.path.exists(board_fen) != None

def save_board(interaction: Interaction, board) -> None:
    board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
    with open(board_fen, 'w') as f:
        f.write(board.fen())

def load_board(interaction: Interaction) -> chess.Board | None:
    board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
    if not os.path.exists(board_fen):
        return None
    with open(board_fen, 'r') as f:
        fen = f.read()
        return chess.Board(fen)

def rm_board(interaction: Interaction) -> None:
    board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
    os.remove(board_fen)

def save_board_image(interaction: Interaction, board, flipped=False) -> None:
    svg_image = svg.board(board, flipped=flipped)
    image_path: str = os.path.join(str(interaction.user.id), "chess_board.png")
    with open(image_path, "wb") as f:
        svg2png(bytestring=svg_image.encode('utf-8'), write_to=f, dpi=300)

def AI_move(board: chess.Board, config) -> chess.Move | None:
    engine = SimpleEngine.popen_uci(STOCKFISH)
    engine.configure({"Skill Level": config[0]})
    best_move = engine.play(board, Limit(depth=config[1], time=config[2])).move
    engine.close()
    return best_move

class ChessCommands(Group):
    def __init__(self):
        super().__init__(name="chess", description="chess commands")

    @command(name="help", description="show weather's functions")
    async def help(self, interaction: Interaction) -> None:
        help = """### Usage:
        /chess <Commands> [settings ...]
### Commands:
  - new [start] [level] [depth] [response_time] - start a new chess game
    - <start> - White, Black; default is White
    - <level> - Integer; default is 0
    - <depth> - Integer; default is 1
    - <reponse_time> - Float; default is 0.1
  - move <legal_move> - move pieces
    - e.g. e4e5, e5, g1f3, ...
  - show - show current chess board 
  - fen - show current board fen
  - analyze [moves] - analyze the current game
    - <moves> - Integer
"""
        await interaction.response.send_message(help)

    start_with = [
        Choice(name="White", value="white"),
        Choice(name="Black", value="black")
    ]

    @command(name='new', description='start a new chess game')
    @choices(start=start_with)
    @describe(level="stockfish levels")
    @describe(depth="stockfish depths")
    @describe(response_time="stockfish response time")
    async def new(self, interaction: Interaction, start: Optional[Choice[str]], level: Optional[int], depth: Optional[int], response_time: Optional[float]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        if start == None:
            start = self.start_with[0]

        save_stockfish_config(interaction, 
                              0 if level == None else level,
                              1 if depth == None else depth,
                              0.1 if response_time == None else response_time)

        board = chess.Board()
        if start.name == "White":
            save_board(interaction, board)
            save_board_image(interaction, board)
            await interaction.response.send_message(file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        config = load_stockfish_config(interaction)
        best_move = AI_move(board, config)

        if best_move == None:
            await interaction.response.send_message("chess - ai has no move")
            return

        board.push(best_move)

        save_board(interaction, board)
        save_board_image(interaction, board, flipped = True)
        await interaction.response.send_message(file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
    
    @command(name='move', description='move pieces')
    async def move(self, interaction: Interaction, move: str) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        board = load_board(interaction)
        if board == None:
            await interaction.response.send_message("chess - Please use /chess new to make a new game")
            return 

        flipped = board.turn == chess.BLACK

        try:
            board.push_san(move)
        except:
            await interaction.response.send_message(f"chess - invalid move {move}")
            return

        if board.is_game_over():
            rm_board(interaction)
            await interaction.response.send_message(f"chess - you win", file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        config = load_stockfish_config(interaction)
        best_move = AI_move(board, config)

        if best_move == None:
            rm_board(interaction)
            await interaction.response.send_message("chess - ai has no move")
            return

        board.push(best_move)

        if board.is_game_over():
            rm_board(interaction)
            await interaction.response.send_message(f"chess - you loss", file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        save_board(interaction, board)
        save_board_image(interaction, board, flipped=flipped)
        await interaction.response.send_message(format(f"chess - {best_move}", header="###"), file=File(os.path.join(str(interaction.user.id), "chess_board.png")))

    @command(name="show", description="show current chess board")
    async def show(self, interaction: Interaction) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        board = load_board(interaction)
        if board == None:
            await interaction.response.send_message("chess - Please use /chess new to make a new game")
            return 

        await interaction.response.send_message(format("chess - current board", header="###"), file=File(os.path.join(str(interaction.user.id), "chess_board.png")))

    @command(name="fen", description="show current board fen")
    async def fen(self, interaction: Interaction) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
        if not os.path.exists(board_fen):
            await interaction.response.send_message("chess -  Please use /chess new to make a new game")
            return
        with open(board_fen, 'r') as f:
            await interaction.response.send_message(f.read())

    @command(name="analyze", description="analyze the current game")
    async def analyze(self, interaction: Interaction, moves: Optional[int]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        board = load_board(interaction)
        if board == None:
            await interaction.response.send_message("chess - Please use /chess new to make a new game")
            return

        if moves == None:
            moves = 5
        
        if moves <= 0:
            await interaction.response.send_message("chess - moves need to be positive number")
            return

        board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
        with open(board_fen, 'r') as f:
            fen = f.read()
            response = requests.get(f"https://explorer.lichess.ovh/masters?fen={fen}&moves={moves}&top_moves={moves}")
            tops = json.loads(response.text)["moves"]
            result = format("⠀moves⠀games⠀⠀white⠀⠀draws⠀⠀black\n", header="###")
            for top in tops:
                white = top["white"]
                draws = top["draws"]
                black = top["black"]
                games = white + draws + black
                rtotal = 1.0 / (white + black + draws)
                white *= rtotal
                draws *= rtotal
                black *= rtotal

                blocks = 24
                result += format(f"{top['uci']:^3} ⠀{games:>3}⠀ [{'█' * int(blocks * white)}{'▒' * int(blocks * draws)}{'░' * int(blocks * black)}]\n", style=Style.BulletedList)
            await interaction.response.send_message(result)
