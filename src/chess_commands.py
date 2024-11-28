import os
import json
from discord import Interaction, File
from typing import Optional
from discord.app_commands import Group, Choice, describe, command, choices
from text_style import format, Style
import requests

import chess
from chess.engine import SimpleEngine, Limit
from chess import svg
from cairosvg import svg2png

def save_stockfish_config(id: int, level: int, depth: int, response_time: float):
    path: str = os.path.join(str(id), "stockfish_config.json")
    with open(path, 'w') as f:
        f.write(f"[{level},{depth},{response_time}]")

def load_stockfish_config(id: int):
    path: str = os.path.join(str(id), "stockfish_config.json")
    with open(path, 'r') as f:
        return json.load(f)

def board_exist(id: int) -> bool:
    board_fen: str = os.path.join(str(id), "board.fen")
    return os.path.exists(board_fen) != None

def save_board(id: int, board) -> None:
    board_fen: str = os.path.join(str(id), "board.fen")
    with open(board_fen, 'w') as f:
        f.write(board.fen())

def load_board(id: int) -> chess.Board | None:
    board_fen: str = os.path.join(str(id), "board.fen")
    if not os.path.exists(board_fen):
        return None
    with open(board_fen, 'r') as f:
        fen = f.read()
        return chess.Board(fen)

def rm_board(id: int) -> None:
    board_fen: str = os.path.join(str(id), "board.fen")
    os.remove(board_fen)

def save_board_image(id: int, board, flipped=False) -> None:
    svg_image = svg.board(board, flipped=flipped)
    image_path: str = os.path.join(str(id), "chess_board.png")
    with open(image_path, "wb") as f:
        svg2png(bytestring=svg_image.encode('utf-8'), write_to=f, dpi=300)

def AI_move(board: chess.Board, config) -> chess.Move | None:
    engine = SimpleEngine.popen_uci("../lib/stockfish")
    engine.configure({"Skill Level": config[0]})
    best_move = engine.play(board, Limit(depth=config[1], time=config[2])).move
    engine.close()
    return best_move

class ChessCommands(Group):
    def __init__(self):
        super().__init__(name="chess", description="chess commands")

    start_with = [
        Choice(name="White", value="white"),
        Choice(name="Black", value="black")
    ]

    @command(name='new', description='start a new chess game')
    @choices(start_with=start_with)
    @describe(level="stockfish levels")
    @describe(depth="stockfish depths")
    @describe(response_time="stockfish response time")
    async def new(self, interaction: Interaction, start_with: Optional[Choice[str]], level: Optional[int], depth: Optional[int], response_time: Optional[float]) -> None:
        if os.path.exists(str(id)) == None:
            await interaction.response.send_message("please use /init to initialize")
            return

        if start_with == None:
            start_with = self.start_with[0]

        save_stockfish_config(interaction.user.id, 
                              0 if level == None else level,
                              1 if depth == None else depth,
                              0.1 if response_time == None else response_time)

        board = chess.Board()
        if start_with.name == "White":
            save_board(interaction.user.id, board)
            save_board_image(interaction.user.id, board)
            await interaction.response.send_message(file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        config = load_stockfish_config(interaction.user.id)
        best_move = AI_move(board, config)

        if best_move == None:
            await interaction.response.send_message("chess - ai has no move")
            return

        board.push(best_move)

        save_board(interaction.user.id, board)
        save_board_image(interaction.user.id, board, flipped = True)
        await interaction.response.send_message(file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
    
    @command(name='move', description='move pieces')
    async def move(self, interaction: Interaction, move: str) -> None:
        board = load_board(interaction.user.id)
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
            rm_board(interaction.user.id)
            await interaction.response.send_message(f"chess - you win", file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        config = load_stockfish_config(interaction.user.id)
        best_move = AI_move(board, config)

        if best_move == None:
            rm_board(interaction.user.id)
            await interaction.response.send_message("chess - ai has no move")
            return

        board.push(best_move)

        if board.is_game_over():
            rm_board(interaction.user.id)
            await interaction.response.send_message(f"chess - you loss", file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
            return

        save_board(interaction.user.id, board)
        save_board_image(interaction.user.id, board, flipped=flipped)
        await interaction.response.send_message(format(f"chess - {best_move}", header="###"), file=File(os.path.join(str(interaction.user.id), "chess_board.png")))

    @command(name='analyze', description='analyze the current game')
    async def analyze(self, interaction: Interaction) -> None:
        if os.path.exists(str(id)) == None:
            await interaction.response.send_message("please use /init to initialize")
            return

        board = load_board(interaction.user.id)
        if board == None:
            await interaction.response.send_message("chess - Please use /chess new to make a new game")
            return

        board_fen: str = os.path.join(str(interaction.user.id), "board.fen")
        with open(board_fen, 'r') as f:
            fen = f.read()
            response = requests.get(f"https://explorer.lichess.ovh/masters?fen={fen}&since=2000&topGames=5&moves=5")
            tops = json.loads(response.text)["moves"]
            result = format("⠀moves  white draws black\n", header="###")
            for top in tops:
                white = top["white"]
                draws = top["draws"]
                black = top["black"]
                rtotal = 1.0 / (white + black + draws)
                white *= rtotal
                draws *= rtotal
                black *= rtotal

                blocks = 20
                result += format(f"{top["uci"]:^5} [{'█' * int(blocks * white)}{'▒' * int(blocks * draws)}{'░' * int(blocks * black)}]\n", style=Style.BulletedList)
            await interaction.response.send_message(result)
