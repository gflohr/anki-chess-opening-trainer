from typing import List, TypedDict

from chess import Color
import chess
from chess.pgn import SKIP, BaseVisitor

from pgn_import.collector import Collector


class PGNError(TypedDict):

	'''Stores an error message with a game number.'''
	error: str
	gameno: int


class Visitor(BaseVisitor):

	'''Collects moves and comments.

	Args:
		collector: The Collector to interact with.
		drop_white_variations: True if only white mainlines should be used.
		drop_black_variations: True if only black mainlines should be used.
	'''
	def __init__(
			self,
			collector: Collector,
			drop_white_variations: bool = False,
			drop_black_variations: bool = False,
	):
		super().__init__()

		self._collector = collector
		self._drop_white = drop_white_variations
		self._drop_black = drop_black_variations

		self._turn: Color = None
		# This is also an indicator that there is an active game.
		self._game_id: str = None
		self._gameno = 0
		self._errors: List[str] = []
		self._fen_before: str = None
		# This is also an indicator that we are not at the beginning of a
		# variation.
		self._last_move: chess.Move = None
		self._fen_after: str = None

	def begin_game(self):
		self._game_id = None
		self._last_move = None

	def visit_board(self, board):
		self._turn = board.turn
		self._fen_after = board.fen()
		if self._game_id is None:
			# There is no need to normalise the fen. We keep the start position
			# merely as an indicator that we are inside of a game.
			self._game_id = self._collector.add_game(board.fen())
		else:
			self._game_id = self._collector.add_move(
				game_id=self._game_id,
				move=self._last_move,
				fen_before=self._fen_before,
				fen_after=self._fen_after)

	def visit_move(self, board, move):
		self._fen_before = board.fen()
		self._last_move = move
		# Do not call the add_move method of the collector here. We wait for
		# visit_board(), so that the FEN is already created.

	def begin_variation(self):
		self._last_move = None
		if self._drop_white and self._turn == chess.BLACK:
			return SKIP

		if self._drop_black and self._turn == chess.WHITE:
			return SKIP

		self._collector.begin_variation()

		return None

	def end_variation(self):
		# Do not notify, when the variation was skipped.
		if self._drop_white and self._turn == chess.BLACK:
			return

		if self._drop_black and self._turn == chess.WHITE:
			return

		self._collector.end_variation()

	def visit_comment(self, comment: str):
		if self._last_move is None:
			self._collector.add_variation_comment(comment)
		else:
			self._collector.add_comment(comment)

	def visit_nag(self, nag: int):
		self._collector.add_nag(nag)

	def handle_error(self, error: Exception):
		self._errors.append({
			'gameno': self._gameno,
			'error': str(error)
		})

	def result(self) -> List[PGNError]:
		return self._errors
