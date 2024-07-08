from typing import List, Literal, Optional

from chess import Board, Move
from chess.pgn import BaseVisitor

from game_node import GameNode


class PositionVisitor(BaseVisitor):


	def __init__(self):
		self.nodes: List[GameNode] = []
		self.fen = Optional[str]
		self.node = Optional[GameNode]

	def begin_game(self) -> None:
		self.node = None
		self.fen = None

	def visit_move(self, board: Board, move: Move) -> None:
		if self.fen is None:
			self.fen = board.fen()

		self.node = GameNode(self.fen, board, move)
		self.nodes.append(self.node)

	def visit_comment(self, comment: str) -> None:
		# Comments at the beginning of the game are currently discarded.
		# This is not strictly necessary but requires some modifications.
		# FIXME!
		if self.node is not None:
			self.node.add_comment(comment)

	def visit_nag(self, nag: int):
		self.node.add_nag(nag)

	def result(self) -> Literal[True]:
		return True

	def get_nodes(self) -> List[GameNode]:
		return self.nodes
