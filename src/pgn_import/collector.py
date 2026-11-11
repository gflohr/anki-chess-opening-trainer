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

	def add_move(self, game_id: str, move: str, fen_before: str, fen_after: str) -> str:
		'''Add a move to the game tree identified by its game id.

		Args:
			game_id: The id of the game as returned by add_game().
			move: The move in UCI notation (e.g. "e7e8q").
			fen_before: The FEN before the move.
			fen_after: The FEN after the move.

		Returns:
			The id of the game to continue with.
		'''
		current = self._current_node
		if current is None:
			raise RuntimeError('Cannot add move without an active game context.')

		chess_move = chess.Move.from_uci(move)

		# Check if the child node already exists (transposition/merging)
		existing_node = None
		for child in current.variations:
			if child.board().fen() == fen_after:
				existing_node = child
				break

		if existing_node:
			node = existing_node
		else:
			node = current.add_variation(chess_move)

		# Advance the tip of the current variation stack branch
		self._current_node = node
		return game_id

	def add_comment(self, comment: str) -> None:
		'''Add a comment to the last added move.'''
		current = self._current_node
		if current:
			current.comment = comment

	def add_nag(self, nag: int) -> None:
		'''Add a NAG to the last added move.'''
		current = self._current_node
		if current:
			current.nags.add(nag)

	def add_variation_comment(self, comment: str) -> None:
		'''Add a comment to the last added game or variation header.'''
		current = self._current_node
		if current:
			current.comment = comment

	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
