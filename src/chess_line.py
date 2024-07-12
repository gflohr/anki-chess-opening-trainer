import json
import html
from typing import List

import chess

from .game_node import GameNode
from .chess_move import ChessMove

class ChessLine:
	def __init__(self, nodes: List[GameNode], game_comments: List[str]):
		self._game_comments = game_comments
		self._fen = nodes[0].fen
		self._moves: List[ChessMove] = []

		initial_moves = nodes[0].moves
		for move in initial_moves:
			self._moves.append(ChessMove(move))

		for i, node in enumerate(nodes):
			if i > 0:
				move = node.moves[-1]
				chess_move = ChessMove(move)
				self._moves.append(chess_move)
				prev_node = nodes[i - 1]
				comments = prev_node.comments[move]
				for comment in comments:
					chess_move.add_comment(comment)

		self._turn = chess.Board(self._fen).turn
		if len(self.moves) & 0x1:
			self._turn = not self._turn

		self._responses: List[ChessMove] = []
		comments = nodes[-1].comments

		for move in nodes[-1].responses:
			chess_move = ChessMove(move)
			self._responses.append(chess_move)

			for comment in comments[move]:
				chess_move.add_comment(comment)

	@property
	def moves(self):
		return self._moves

	@property
	def fen(self):
		return self._fen

	@property
	def game_comments(self):
		return self._game_comments

	@property
	def responses(self):
		return self._responses

	@property
	def turn(self):
		return self._turn

	def to_json(self) -> str:
		chess_line = {
			'fen': self.fen,
			'game_comments': self.game_comments,
			'moves': list(map(lambda move: move.dump(), self._moves)),
		}

		return json.dumps(chess_line)

	def render_question(self) -> str:
		board = chess.Board(self._fen)
		rendered = ''

		if board.turn == chess.BLACK:
			rendered += f'{board.fullmove_number}...'

		for chess_move in self._moves:
			if board.turn == chess.WHITE:
				rendered += f'{board.fullmove_number}.'

			rendered += ' ' + board.san_and_push(chess_move.move)

		return rendered

	def render_answer(self) -> str:
		board = chess.Board(self.fen)

		for chess_move in self._moves:
			board.push(chess_move.move)

		prefix = str(board.fullmove_number) + '.'
		if board.turn == chess.BLACK:
			prefix += '..'

		answers: List[str] = []
		for response in self.responses:
			san_response = board.san(response.move)
			rendered = prefix + ' ' + san_response
			comments = response.comments
			if len(comments):
				rendered += ' '
				rendered += '<em>' + html.escape(' '.join(comments)) + '</em>'

			answers.append(rendered)

		return '\n'.join(answers)

