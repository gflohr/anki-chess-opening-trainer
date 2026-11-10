from typing import List, TypedDict

from chess.pgn import BaseVisitor

from pgn_import.collector import Collector


class PGNError(TypedDict):

	'''Stores an error message with a game number.'''
	error: str
	gameno: int


class Visitor(BaseVisitor):

	'''Collects moves and comments.'''
	def __init__(self, collector: Collector):
		super().__init__()

		self._collector = collector
		self._startpos: str = None
		self._gameno = 0
		self._errors: List[str] = []

	def begin_game(self):
		self._startpos = None

	def visit_board(self, board):
		if self._startpos is None:
			# There is no need to normalise the fen. We keep the start position
			# merely as an indicator that we are inside of a game.
			self._startpos = board.fen()
			self._collector.add_game(board.fen())

	def handle_error(self, error: Exception):
		self._errors.append({
			'gameno': self._gameno,
			'error': str(error)
		})

	def result(self) -> List[PGNError]:
		return self._errors
