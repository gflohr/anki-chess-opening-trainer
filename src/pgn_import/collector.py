from chess import Color
import chess.pgn
from typing import Dict


class Collector:
	'''Collects and aggregates PGN chess games for Anki note generation.'''

	def __init__(self, colour: Color):
		if colour == chess.WHITE:
			self._colour = 'White'
		else:
			self._colour = 'Black'
		self._games: Dict[str, chess.pgn.Game] = {}
		# The minimum (full) move number seen for each normalised FEN. We
		# assume that a lower move number is more accurate.
		self._move_numbers: Dict[str, int] = {}

	def games(self) -> Dict[str, chess.pgn.Game]:
		'''Get all collected games.

		Games are distinguished by their normalised starting position (ignoring
		the move number and halfmove count). The returned dictionary keys are
		reconstructed FENs including the halfmove count (0) and the minimum
		move number recorded for that position.

		Returns:
			A dictionary mapping the reconstructed FEN keys to the collected games.
		'''
		return {
			f'{fen} 0 {self._move_numbers[fen]}': game
			for fen, game in self._games.items()
		}

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
		if not fen in self._games:
			starting_fen = self._normalise_fen(initial_fen)
			if fen == starting_fen:
				self._games[fen] = chess.pgn.Game({
					'Colour': self._colour
				})
				self._move_numbers[fen] = 1
			else:
				self._games[fen] = chess.pgn.Game({
					'Colour': self._colour,
					'Setup': '1',
					'FEN': initial_fen,
				})
				# Remember the "best" full move number for the position.
				move_number = self._games[fen].board().fullmove_number
				if move_number < self._move_numbers[fen]:
					self._move_numbers[fen] = move_number

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

	def add_variation_comment(self, comment: str) -> None:
		'''Add a comment to the last added game or variation.

		Args:
			comment: The textual comment
		'''
		pass

	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
