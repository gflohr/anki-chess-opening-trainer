from typing import List, Literal, Optional

from chess import Board, Move
from chess.pgn import BaseVisitor

from game_node import GameNode


class PositionVisitor(BaseVisitor):

	def __init__(self):
		self._nodes: List[GameNode] = []
		self._fen = Optional[str]
		self._node = Optional[GameNode]
		self._game_comments: List[str] = []

	def begin_game(self) -> None:
		self._node = None
		self._fen = None

	def visit_move(self, board: Board, move: Move) -> None:
		if self._fen is None:
			self._fen = board.fen()

		self._node = GameNode(self._fen, board, move)
		self._nodes.append(self._node)

	def visit_comment(self, comment: str) -> None:
		if self._node is None:
			self._game_comments.append(comment)
		else:
			self._node.add_comment(comment)

	def visit_nag(self, nag: int):
		self._node.add_nag(nag)

	def result(self) -> Literal[True]:
		return True

	@property
	def nodes(self) -> List[GameNode]:
		return self._nodes

	@property
	def game_comments(self):
		return self._game_comments
