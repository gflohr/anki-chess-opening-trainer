from typing import Iterator

from chess import Color
from chess.pgn import Game, GameNode
from collections import deque

from utils import _normalise_fen


class CardGenerator:
	def __init__(self, game: Game, colour: Color) -> None:
		self._game = game
		self._colour = colour
		self._questions: dict[str, GameNode] = {}

		queue: deque[GameNode] = deque([self._game])

		while queue:
			node = queue.popleft()
			board = node.board()
			fen = board.fen()
			norm_fen = _normalise_fen(fen)

			if board.turn == self._colour and node.variations and norm_fen not in self._questions:
				self._questions[norm_fen] = node

			for child in node.variations:
				queue.append(child)

	def cards(self) -> Iterator[tuple[str, GameNode]]:
		for fen, node in self._questions.items():
			if node.variations:
				yield fen, node
