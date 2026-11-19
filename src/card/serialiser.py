from typing import NotRequired, TypedDict

import chess
from chess.pgn import Game

class GameDump(TypedDict):
	# The optional starting position as a FEN.
	f: NotRequired[str]

class Serialiser:
	def serialise(self, game: Game) -> GameDump:
		dump = {}

		fen = game.board().fen()
		if not self._normalise_fen(fen) == self._normalise_fen(chess.STARTING_FEN):
			dump['f'] = fen

		return dump

	# FIXME! This must become a utility function.
	def _normalise_fen(self, fen: str) -> str:
		return ' '.join(fen.split()[:4])

