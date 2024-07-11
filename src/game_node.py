from __future__ import annotations
from typing import Dict, List

import chess
from chess import Color, Board, Move


class GameNode:
	def __init__(self, fen: str, board: Board, move: Move):
		self._fen = fen
		position = Board(fen=self.fen)

		self._moves = board.move_stack.copy()
		self._san_moves: List[str] = []
		for i, prev_move in enumerate(board.move_stack.copy()):
			san = position.san(prev_move)

			if i == 0 and position.turn == chess.BLACK:
				prefix = str(position.fullmove_number) + '...'
			elif position.turn == chess.WHITE:
				prefix = str(position.fullmove_number) + '. '
			else:
				prefix = ''

			self._san_moves.append(prefix + san)
			position.push(prev_move)

		self._colour = board.turn
		self._responses = [move]
		self._san_responses = [position.san(move)]
		self._comments: Dict[Move, List[str]] = { move: [] }
		self._nags: List[int] = []

	def add_comment(self, comment: str):
		self._comments[self._move].append(comment)

	def add_nag(self, nag: int):
		self._nags.append(nag)

	def signature(self) -> str:
		if len(self._san_moves):
			return self._fen + ' ' + self.signature_v1()
		else:
			return self._fen

	def signature_v1(self) -> str:
		return ' '.join(map(str, self._san_moves))

	def previous_signatures(self) -> List[str]:
		signatures: List[str] = []
		_san_moves = self._san_moves
		while len(_san_moves) > 1:
			_san_moves = _san_moves[:-2]
			tokens = [self._fen] + list(map(str, _san_moves))
			signatures.append(' '.join(tokens))

		signatures.reverse()

		return signatures

	@property
	def san_responses(self):
		return self._san_responses

	def merge(self, other: GameNode):
		# We assume that the move stack is equal.
		for response in other._responses:
			if response not in self._responses:
				self._responses.append(response)
		for response in other._san_responses:
			if response not in self._san_responses:
				self._san_responses.append(response)

		for move, comments in other._comments.items():
			self._comments[move] = comments

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
	def fen(self):
		return self._fen

	@property
	def moves(self):
		return self._moves

	@property
	def san_moves(self):
		return self._san_moves

	@property
	def comments(self):
		return self._comments
