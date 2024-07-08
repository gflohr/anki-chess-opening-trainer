from __future__ import annotations
from typing import List

import chess
from chess import Color, Board, Move


class GameNode:
	def __init__(self, initial_fen: str, board: Board, move: Move):
		self.initial_fen = initial_fen
		position = Board(fen=initial_fen)
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

		self.colour = board.turn
		self.responses = [position.san(move)]
		self.comments: List[str] = []
		self.nags: List[int] = []

	def add_comment(self, comment: str):
		self.comments.append(comment)

	def add_nag(self, nag: int):
		self.nags.append(nag)

	def get_signature(self) -> str:
		moves_signature = ':'.join(map(str, self.moves))
		return self.initial_fen + ':' + moves_signature

	def get_previous_signatures(self) -> List[str]:
		signatures: List[str] = []
		moves = self.moves
		while len(moves) > 1:
			moves = moves[:-2]
			tokens = [self.initial_fen] + list(map(str, moves))
			signatures.append(':'.join(tokens))

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

		for nag in other.nags:
			if nag not in self.nags:
				self.nags.append(nag)

	def get_nags(self) -> List[int]:
		return self.nags

	def set_nags(self, nags: List[int]):
		self.nags = nags

	def get_colour(self) -> Color:
		return self.colour
