from chess import Color
import chess.pgn
from typing import Dict, List, Optional


class Collector:
	'''Collector and aggregator for PGN chess games for Anki note generation.'''

	def __init__(self, colour: Color) -> None:
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

		Args:
			initial_fen: The initial position as a FEN.

		Returns:
			The id (normalised FEN) of the game.
		'''
		fen = self._normalise_fen(initial_fen)
		board = chess.Board(initial_fen)
		move_number = board.fullmove_number

		if fen not in self._games:
			if initial_fen == chess.STARTING_FEN:
				self._games[fen] = chess.pgn.Game({
					'Colour': self._colour,
				})
			else:
				self._games[fen] = chess.pgn.Game({
					'Colour': self._colour,
					'SetUp': '1',
					'FEN': initial_fen,
				})
				self._games[fen].setup(board)
			self._move_numbers[fen] = move_number
		else:
			if move_number < self._move_numbers[fen]:
				self._move_numbers[fen] = move_number
				if initial_fen != chess.STARTING_FEN:
					self._games[fen].headers['SetUp'] = '1'
					self._games[fen].headers['FEN'] = initial_fen
					self._games[fen].setup(board)

		# Reset the stack for the new game context
		return fen

	def add_move(self, game_id: str, move: chess.Move, fen_before: str, fen_after: str) -> str:
		'''Add a move to the game tree identified by its game id.

		Args:
			game_id: The id of the game as returned by add_game().
			move: The move as a chess.Move object.
			fen_before: The FEN before the move.
			fen_after: The FEN after the move.

		Returns:
			The id of the game to continue with.
		'''
		return game_id

	def add_comment(self, comment: str) -> None:
		'''Add a comment to the last added move.'''
		pass

	def add_nag(self, nag: int) -> None:
		'''Add a NAG to the last added move.'''
		pass

	def add_variation_comment(self, comment: str) -> None:
		'''Add a comment to the last added game or variation header.'''
		pass

	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
