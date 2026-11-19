from typing import NotRequired, TypedDict

import chess
from chess.pgn import Game, GameNode


class GameNodeDump(TypedDict):
	# The move leading here (UCI)
	m: str
	# Child variations from this position
	v: NotRequired[list['GameNodeDump']]


class GameDump(TypedDict):
	# The optional starting position as a FEN.
	f: NotRequired[str]
	# Root variations from the starting position
	v: NotRequired[list[GameNodeDump]]


class Serialiser:
	def serialise(self, game: Game) -> GameDump:
		dump: GameDump = {}

		fen = game.board().fen()
		if self._normalise_fen(fen) != self._normalise_fen(chess.STARTING_FEN):
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
			child_variations = self._serialise_game_node(variation)
			if child_variations:
				node_dump['v'] = child_variations

			variations.append(node_dump)

		return variations if variations else None

	# FIXME! This must become a utility function.
	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])
