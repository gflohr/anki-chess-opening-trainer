from typing import NotRequired, TypedDict

import chess
from chess.pgn import Game, GameNode

from utils import normalise_fen


class GameNodeDump(TypedDict):
	# The move leading here (UCI)
	m: str
	# Child variations from this position
	v: NotRequired[list['GameNodeDump']]
	# Optional starting comment.
	s: NotRequired[str]
	# Optional comment.
	c: NotRequired[str]
	# NAGs.
	n: NotRequired[list[int]]


class GameDump(TypedDict):
	# The optional starting position as a FEN.
	f: NotRequired[str]
	# Root variations from the starting position
	v: NotRequired[list[GameNodeDump]]


class CardSerialiser:
	def serialise(self, game: Game) -> GameDump:
		dump: GameDump = {}

		fen = game.board().fen()
		if normalise_fen(fen) != normalise_fen(chess.STARTING_FEN):
			dump['f'] = fen

		variations = self._serialise_game_node(game)
		if variations:
			dump['v'] = variations

		return dump

	def _serialise_game_node(self, node: GameNode) -> list[GameNodeDump] | None:
		if not node.variations:
			return None

		variations: list[GameNodeDump] = []
		for variation in node.variations:
			if variation.move is None:
				continue

			node_dump: GameNodeDump = {
				'm': variation.move.uci(),
			}

			if len(variation.starting_comment):
				node_dump['s'] = variation.starting_comment
			if len(variation.comment):
				node_dump['c'] = variation.comment
			if len(variation.nags):
				node_dump['n'] = list(variation.nags)

			if len(variation.starting_comment):
				pass

			child_variations = self._serialise_game_node(variation)
			if child_variations:
				node_dump['v'] = child_variations

			variations.append(node_dump)

		return variations if variations else None
