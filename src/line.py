import json
from typing import List

from chess import Move

from .game_node import GameNode


class Line:
	def __init__(self, nodes: List[GameNode], game_comments: List[str]):
		self._nodes = nodes
		self._game_comments = game_comments

	@property
	def san_responses(self) -> List[Move]:
		return self._nodes[-1].san_responses

	@property
	def nodes(self) -> List[GameNode]:
		return self._nodes

	@property
	def fen(self) -> str:
		return self._nodes[0].fen

	@property
	def game_comments(self) -> List[str]:
		return self._game_comments

	def to_json(self) -> str:
		line = {
			'fen': self.fen,
		}

		return json.dump(line)
