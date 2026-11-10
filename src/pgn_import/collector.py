import chess.pgn
from typing import Any, Dict


class Collector:
	'''Collects and aggregates PGN chess games for Anki note generation.'''

	def __init__(self):
		self.games: Dict[str, chess.pgn.Game] = {}

	def add_game(self, game: chess.pgn.Game) -> None:
		'''Process a parsed PGN game.'''
		fen = self.normalise_fen(game.board().fen())
		if not fen in self.games:
			self.games[fen] = game

	def normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
