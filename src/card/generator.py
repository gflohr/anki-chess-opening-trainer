from chess import Color
from chess.pgn import Game, GameNode
from collections import deque

from utils import _normalise_fen


class CardGenerator:
	def __init__(self, game: Game, colour: Color) -> None:
		self._game = game
		self._colour = colour

		seen_fens: dict[str, GameNode] = {}
		queue: deque[GameNode] = deque([self._game])

		while queue:
			node = queue.popleft()
			board = node.board()
			fen = board.fen()
			norm_fen = _normalise_fen(fen)

			if board.turn == self._colour and node.variations and norm_fen not in seen_fens:
				seen_fens[norm_fen] = node

			for child in node.variations:
				queue.append(child)

