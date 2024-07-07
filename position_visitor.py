from __future__ import annotations
from typing import Dict, List, Literal, Optional, cast

from chess import Color, Board, Move
from chess.pgn import BaseVisitor, SkipType


class Node:
	def __init__(self, fen: str, move_stack: List[Move], move: Move):
		self.fen = fen

		moves = move_stack.copy()
		moves.append(move)

		self.moves = move_stack
		self.responses = [move]
		self.comments: List[str] = []
		self.nags: List[int] = []

	def add_comment(self, comment: str):
		self.comments.append(comment)

	def add_nag(self, nag: int):
		self.nags.append(nag)

	def get_signature(self) -> str:
		moves_signature = ':'.join(map(str, self.moves))
		return self.fen + ':' + moves_signature

	def merge(self, other: Node):
		# We assume that the move stack is equal.
		for response in other.responses:
			if response not in self.responses:
				self.responses.append(response)

		for comment in other.comments:
			if comment not in self.comments:
				self.comments.append(comment)

		for nag in other.nags:
			if nag not in self.nags:
				self.nags.append(nag)

	def get_nags(self) -> List[int]:
		return self.nags

	def set_nags(self, nags: List[int]):
		self.nags = nags


class PositionVisitor(BaseVisitor):


	def __init__(self):
		self.nodes: List[Node] = []
		self.fen = Optional[str]
		self.node = Optional[Node]

	def begin_game(self) -> None:
		self.node = None
		self.fen = None

	def visit_move(self, board: Board, move: Move) -> None:
		if self.fen is None:
			self.fen = board.fen()

		self.node = Node(self.fen, board.move_stack.copy(), move)
		self.nodes.append(self.node)

	def visit_comment(self, comment: str) -> None:
		# Comments at the beginning of a game do not make sense here because
		# they could be before move 1, before move 20, before ...
		if self.node is not None:
			self.node.add_comment(comment)

	def visit_nag(self, nag: int):
		self.node.add_nag(nag)

	def result(self) -> Literal[True]:
		return True

	def get_nodes(self) -> List[Node]:
		return self.nodes
