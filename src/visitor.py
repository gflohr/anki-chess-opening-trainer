# Copyright (C) 2023-2026 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import typing
from typing import Dict, Literal, cast

import chess
from chess import Color, Board, STARTING_FEN
from chess.pgn import BaseVisitor, Game

from .answer import Answer
from .question import Question


# Monkey-patch the piece_symbol() method.
def i18n_piece_symbol(piece_type: chess.PieceType) -> str:
	piece_symbols = [
		None,
		# TRANSLATORS: This is the letter to use for a pawn.
		_('p'),
		# TRANSLATORS: This is the letter to use for a knight.
		_('n'),
		# TRANSLATORS: This is the letter to use for a bishop.
		_('b'),
		# TRANSLATORS: This is the letter to use for a rook.
		_('r'),
		# TRANSLATORS: This is the letter to use for a queen.
		_('q'),
		# TRANSLATORS: This is the letter to use for a king.
		_('k'),
	]
	return typing.cast(str, piece_symbols[piece_type])


class PositionVisitor(BaseVisitor):

	# pylint: disable=too-many-instance-attributes
	def __init__(self, colour, web_path: str, game_node: Game = None):
		self.colour: Color = colour
		self.initial: Board
		self.has_board = False
		self.seen: Dict[str, str] = {}
		self.cards: Dict[str, Question] = {}
		self.last_question_key = None
		self.accumulated_comments = []
		self.my_move = True
		self.web_path = web_path

		# Store the base game template to extract/preserve original headers
		self.game_node = game_node

	def begin_game(self) -> None:
		self.has_board = False

	def visit_board(self, board) -> None:
		if not self.has_board:
			self.initial = board.copy()
			self.has_board = True

	def visit_move(self, board, move) -> None:
		if board.turn == self.colour:
			if board.ply():
				saved_piece_symbol = chess.piece_symbol
				chess.piece_symbol = i18n_piece_symbol
				text = self.initial.variation_san(board.move_stack)
				chess.piece_symbol = saved_piece_symbol
			else:
				text = ''

			question_key = " ".join(board.fen().split()[:4])

			# Construct PGN representation leading up to the current move.
			current_game = Game()
			if self.game_node:
				current_game.setup(self.game_node.board())
			elif hasattr(self, 'initial'):
				current_game.setup(self.initial)

			# Populate nodes from board stack.
			node = current_game
			temp_board = self.initial.copy()
			for m in board.move_stack:
				node = node.add_variation(m)
				temp_board.push(m)

			# Include the current visit move as well.
			node = node.add_variation(move)

			answer_board = board.copy()
			saved_piece_symbol = chess.piece_symbol
			chess.piece_symbol = i18n_piece_symbol
			san = answer_board.san(move)
			chess.piece_symbol = saved_piece_symbol
			answer_board.push(move)
			fen = answer_board.fen
			if fen in self.seen:
				# Already seen.
				return

			answer = Answer(
				san,
				board=answer_board,
				game=current_game,
				colour=self.colour,
				web_path=self.web_path
			)

			if question_key not in self.cards:
				turn = not board.turn
				question = self.cards[question_key] = Question(
					text,
					turn=turn,
					colour=self.colour,
					web_path=self.web_path,
				)

				for comment in self.accumulated_comments:
					question.add_comment(comment)
				self.accumulated_comments = []
				question.set_board(board.copy())
			elif answer.find(self.cards[question_key].answers):
				return

			self.cards[question_key].add_answer(answer)
			self.my_move = True
			self.last_question_key = question_key
		else:
			self.accumulated_comments = []
			self.my_move = False

	def visit_comment(self, comment: str) -> None:
		if self.last_question_key and isinstance(self.cards[self.last_question_key], Question):
			question: Question = cast(Question, self.cards[self.last_question_key])
			if self.my_move:
				question.answers[-1].add_comment(comment)
			elif self.accumulated_comments:
				self.accumulated_comments.append(comment)

	def result(self) -> Literal[True]:
		return True
