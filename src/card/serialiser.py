from typing import NotRequired, TypedDict

import chess
from chess.pgn import Game, GameNode

class GameNodeDump(TypedDict):
	# The move leading here
	m: str

class GameDump(TypedDict):
	# The optional starting position as a FEN.
	f: NotRequired[str]
	v: NotRequired[list[GameNodeDump]]

class Serialiser:
	def serialise(self, game: Game) -> GameDump:
		dump = {}

		fen = game.board().fen()
		if not self._normalise_fen(fen) == self._normalise_fen(chess.STARTING_FEN):
			dump['f'] = fen

		variations = self._serialise_game_node(game)
		if variations:
			dump['v'] = variations

		return dump

	def _serialise_game_node(self, node: GameNode) -> GameNodeDump | None:
		if node.variations:
			variations = []
			for variation in node.variations:
				variations.append({
					'm': variation.uci()
				})
			return variations

	# FIXME! This must become a utility function.
	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])

