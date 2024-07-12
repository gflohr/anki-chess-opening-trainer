from typing import List, Literal, Optional

from chess import Board, Move
from chess.pgn import BaseVisitor

from game_node import GameNode


class PositionVisitor(BaseVisitor):

	def __init__(self):
		self.nodes: List[GameNode] = []
		self.fen = Optional[str]
		self.node = Optional[GameNode]
		self._game_comments: List[str] = []

	def begin_game(self) -> None:
		self.node = None
		self.fen = None

	def visit_move(self, board: Board, move: Move) -> None:
		if self.fen is None:
			self.fen = board.fen()

		self.node = GameNode(self.fen, board, move)
		self.nodes.append(self.node)

	def visit_comment(self, comment: str) -> None:
		if self.node is None:
			self._game_comments.append(comment)
		else:
			self.node.add_comment(comment)

	def visit_nag(self, nag: int):
		self.node.add_nag(nag)

	def result(self) -> Literal[True]:
		return True

	# FIXME! Make this a property!
	def get_nodes(self) -> List[GameNode]:
		return self.nodes

	@property
	def game_comments(self):
		return self._game_comments
