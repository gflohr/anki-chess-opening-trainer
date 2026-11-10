import chess.pgn
from typing import Any, Dict


class Collector:
	'''Collects and aggregates PGN chess games for Anki note generation.'''

	def __init__(self):
		self.games: Dict[str, Any] = {}

	def add_game(self, game: chess.pgn.Game) -> None:
		'''Process a parsed PGN game.'''
		pass

	def normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
