from typing import Dict

import chess.pgn
from chess import Board, Color

from utils import normalise_fen

# FIXME! The code raises exception if internal assumptions fail. However, these
# exception will not be helpful at all when presented to the user. Define
# some public properties like the game number, the game node, and the move
# being applied so that a post-mortem analysis can produce better error
# messages.


class Collector:
	"""Collector and aggregator for PGN chess games for Anki note generation."""

	def __init__(self, colour: Color) -> None:
		self._colour = colour
		self._games: Dict[str, chess.pgn.Game] = {}
		# The minimum (full) move number seen for each normalised FEN. We
		# assume that a lower move number is more accurate.
		self._move_numbers: Dict[str, int] = {}
		# All encountered positions, mapping FEN strings to game nodes.
		self._seen: Dict[str, chess.pgn.GameNode] = {}
		self._starting_fen = normalise_fen(chess.STARTING_FEN)
		# The current node is either a game or a position after a move.
		self._current_node = None

	def games(self) -> Dict[str, chess.pgn.Game]:
		"""Get all collected games.

		Games are distinguished by their normalised starting position (ignoring
		the move number and halfmove count). The returned dictionary keys are
		reconstructed FENs including the halfmove count (0) and the minimum
		move number recorded for that position.

		Returns:
			A dictionary mapping the reconstructed FEN keys to the collected games.
		"""
		return {
			f'{fen} 0 {self._move_numbers[fen]}': game
			for fen, game in self._games.items()
		}

	def add_game(self, board: Board) -> str:
		"""Add a new game with the given start position. If there is already a
		game with that start position, it is merged into the existing game
		instead.

		Args:
			initial_fen: The initial position as a FEN.

		Returns:
			The id (normalised FEN) of the game.
		"""
		initial_fen = board.fen()
		fen = normalise_fen(initial_fen)
		move_number = board.fullmove_number

		# If we've seen this position before, map fen to the canonical
		# normalised key.
		if fen in self._seen:
			self._current_node = self._seen[fen]
			return normalise_fen(self._seen[fen].root().board().fen())

		if fen not in self._games:
			if fen == self._starting_fen:
				self._games[fen] = chess.pgn.Game(
					{
						'Colour': self._colour_as_string(self._colour),
					}
				)
			else:
				self._games[fen] = chess.pgn.Game(
					{
						'Colour': self._colour_as_string(self._colour),
						'SetUp': '1',
						'FEN': initial_fen,
					}
				)
				self._games[fen].setup(board)
			self._seen[fen] = self._games[fen]
			self._current_node = self._games[fen]
			self._move_numbers[fen] = move_number
		else:
			if move_number < self._move_numbers[fen]:
				self._move_numbers[fen] = move_number
				if fen != self._starting_fen:
					self._games[fen].setup(board)

		return fen

	def add_move(
		self, game_id: str, move: chess.Move, fen_before: str, fen_after: str
	) -> str:
		"""Add a move to the game tree identified by its game id.

		Args:
			game_id: The id of the game as returned by add_game().
			move: The move as a chess.Move object.
			fen_before: The FEN before the move.
			fen_after: The FEN after the move.

		Returns:
			The id of the game to continue with.
		"""
		fen = normalise_fen(fen_before)
		if fen not in self._seen:
			raise Exception('Corrupted state, parent position not found!')

		parent = self._seen[fen]
		new_game_id = self._find_game_id(parent)
		if parent.has_variation(move):
			self._current_node = parent.variation(move)
			return new_game_id

		self._current_node = parent.add_variation(move)

		norm_fen = normalise_fen(fen_after)
		if norm_fen not in self._seen:
			# Do not overwrite older entries.
			self._seen[norm_fen] = self._current_node

		return new_game_id

	def add_comment(self, comment: str) -> None:
		"""Add a comment to the last added move, avoiding duplicates."""
		if not self._current_node:
			return

		current = self._current_node.comment
		if not current:
			self._current_node.comment = comment
		else:
			# Split existing concatenated comments using {} as the separator.
			comments = current.split('{}')
			if comment not in comments:
				self._current_node.comment = self._current_node.comment + '{}' + comment

	def add_nag(self, nag: int) -> None:
		"""Add a NAG to the last added move."""
		if not self._current_node:
			return

		self._current_node.nags.add(nag)

	def add_variation_comment(self, comment: str) -> None:
		"""Add a comment to the last added game or variation header."""
		if not self._current_node:
			return

		current = self._current_node.starting_comment
		if not current:
			self._current_node.starting_comment = comment
		else:
			# Split existing concatenated comments using {} as the separator.
			comments = current.split('{}')
			if comment not in comments:
				self._current_node.starting_comment = (
					self._current_node.starting_comment + '{}' + comment
				)

	def _find_game_id(self, node: chess.pgn.GameNode) -> str:
		game_id = normalise_fen(node.root().board().fen())

		if game_id not in self._games:
			raise Exception('Game graph corrupt! Root position not found!')

		return game_id

	def _colour_as_string(self, colour: Color) -> str:
		if colour == chess.BLACK:
			return 'Black'
		else:
			return 'White'
