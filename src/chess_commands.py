import os
import json
from discord import Interaction, File
from typing import Optional
from discord.app_commands import Group, Choice, command, describe, choices
from text_style import Style, format

import chess
import chess.engine
import chess.svg
import cairosvg

def board_exist(id: int) -> bool:
    board_fen: str = os.path.join(str(id), "board.fen")
    return os.path.exists(board_fen) != None

def save_board(id: int, board):
    board_fen: str = os.path.join(str(id), "board.fen")
    with open(board_fen, 'w') as f:
        f.write(board.fen())

def load_board(id: int) -> chess.Board | None:
    board_fen: str = os.path.join(str(id), "board.fen")
    if os.path.exists(board_fen) == None:
        return None
    with open(board_fen, 'r') as f:
        fen = f.read()
        return chess.Board(fen)

def save_board_image(id: int, board, flipped=False) -> None:
    svg_image = chess.svg.board(board, flipped=flipped)
    image_path: str = os.path.join(str(id), "chess_board.png")
    with open(image_path, "wb") as f:
        cairosvg.svg2png(bytestring=svg_image.encode('utf-8'), write_to=f, dpi=300)

class ChessCommands(Group):
    def __init__(self):
        super().__init__(name="chess", description="chess commands")

    start_with = [
                Choice(name="White", value="white"),
                Choice(name="Black", value="black")
            ]

    @command(name='new', description='start a new chess game')
    @choices(start_with=start_with)
    async def new(self, interaction: Interaction, start_with: Optional[Choice[str]]) -> None:
        if start_with == None:
            start_with = self.start_with[0]

        if os.path.exists(str(id)) == None:
            await interaction.response.send_message("please use /init to initialize")
            return

        board = chess.Board()
        save_board(interaction.user.id, board)
        save_board_image(interaction.user.id, board, flipped=start_with.name == "Black")
        await interaction.response.send_message(file=File(os.path.join(str(interaction.user.id), "chess_board.png")))
    

    @command(name='move', description='move pieces')
    async def move(self, interaction: Interaction, move: str) -> None:
        board = load_board(interaction.user.id)
        if board == None:
            await interaction.response.send_message("chess - here is no game")
            return 

        flipped = board.turn == chess.BLACK

        try:
            board.push_san(move)
        except:
            await interaction.response.send_message(f"chess - invalid move {move}")
            return

        engine = chess.engine.SimpleEngine.popen_uci("../lib/stockfish")
        result = engine.analyse(board, chess.engine.Limit(time=0.7))
        if result == None:
            return
        best_move = result.get("pv")[0] # TODO: choice some random move
        board.push(best_move)
        engine.close()

        save_board(interaction.user.id, board)
        save_board_image(interaction.user.id, board, flipped=flipped)
        await interaction.response.send_message(format(f"ai move {best_move}", header="###"), file=File(os.path.join(str(interaction.user.id), "chess_board.png")))

