from __future__ import annotations
from typing import List

import chess
from chess import Color, Board, Move


class GameNode:
	def __init__(self, fen: str, board: Board, move: Move):
		self._fen = fen
		position = Board(fen=self.fen)

		# FIXME! We also need the original moves! Rename moves and responses
		# to san_moves and san_responses, and then introduce new properties
		# for the raw versions.
		self.moves: List[str] = []
		for i, prev_move in enumerate(board.move_stack.copy()):
			san = position.san(prev_move)

			if i == 0 and position.turn == chess.BLACK:
				prefix = str(position.fullmove_number) + '...'
			elif position.turn == chess.WHITE:
				prefix = str(position.fullmove_number) + '. '
			else:
				prefix = ''

			self.moves.append(prefix + san)
			position.push(prev_move)

		self._colour = board.turn
		self.responses = [position.san(move)]
		self.comments: List[str] = []
		self._nags: List[int] = []

	def add_comment(self, comment: str):
		self.comments.append(comment)

	def add_nag(self, nag: int):
		self._nags.append(nag)

	def get_signature(self) -> str:
		if len(self.moves):
			return self._fen + ' ' + self.get_signature_v1()
		else:
			return self._fen

	def get_signature_v1(self) -> str:
		return ' '.join(map(str, self.moves))

	def get_previous_signatures(self) -> List[str]:
		signatures: List[str] = []
		moves = self.moves
		while len(moves) > 1:
			moves = moves[:-2]
			tokens = [self._fen] + list(map(str, moves))
			signatures.append(' '.join(tokens))

		signatures.reverse()

		return signatures

	def get_responses(self) -> List[Move]:
		return self.responses

	def merge(self, other: GameNode):
		# We assume that the move stack is equal.
		for response in other.responses:
			if response not in self.responses:
				self.responses.append(response)

		for comment in other.comments:
			if comment not in self.comments:
				self.comments.append(comment)

		for nag in other._nags:
			if nag not in self._nags:
				self._nags.append(nag)

	@property
	def nags(self) -> List[int]:
		return self._nags

	@nags.setter
	def nags(self, nags: List[int]):
		self._nags = nags

	@property
	def colour(self):
		return self._colour

	@property
	def fen(self) -> str:
		return self._fen
