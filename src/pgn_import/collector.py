import chess.pgn
from typing import Any, Dict


class Collector:
	'''Collects and aggregates PGN chess games for Anki note generation.'''

	def __init__(self):
		self.games: Dict[str, chess.pgn.Game] = {}

	def add_game(self, initial_fen: str) -> str:
		'''Add a new game with the given start position. If there is already a
		game with that start position, it is merged into the existing game
		instead.

		Returns the id of the created or merged game.

		Args:
			initial_fen: The initial position as a FEN.

		Returns:
			The id of the game.
		'''
		fen = self._normalise_fen(initial_fen)
		if not fen in self.games:
			self.games[fen] = chess.pgn.Game()

		return fen

	def add_move(self, game_id: str, move: str, fen_before: str, fen_after: str) -> str:
		'''Add a move to the game tree identified by its game id.

		Args:
			game_id: The id of the game as returned by add_game().
			move: The move in UCI notation (e.g. "e7e8q").
			fen_before: The FEN before the move.
			fen_after: The FEN after the move.

		Returns:
			The id of the game to continue with. This may differ from the
			original game id.
		'''
		pass

	def add_comment(self, comment: str) -> None:
		'''Add a comment to the last added move.

		Args:
			comment: The textual comment
		'''
		pass

	def add_nag(self, nag: int) -> None:
		'''Add a NAG to the last added move.

		Args:
			nag: The id (1-255)
		'''
		pass

	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
