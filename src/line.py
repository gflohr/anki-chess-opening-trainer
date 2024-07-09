from typing import List

from chess import Move

from .game_node import GameNode


class Line:
	def __init__(self, nodes: List[GameNode]):
		self._nodes = nodes

	@property
	def san_responses(self) -> List[Move]:
		return self._nodes[-1].san_responses

	@property
	def nodes(self) -> List[GameNode]:
		return self._nodes

	@property
	def fen(self) -> str:
		return self._nodes[0].fen
