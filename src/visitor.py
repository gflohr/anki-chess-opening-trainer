# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import typing
from typing import Literal

import chess
from chess import Color
from chess.pgn import BaseVisitor

from .answer import Answer
from .page import Page
from .question import Question


# Monkey-patch the piece_symbol() method.
def i18n_piece_symbol(piece: chess.PieceType):
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
	return typing.cast(str, piece_symbols[piece])


class PositionVisitor(BaseVisitor):
	def __init__(self, colour):
		self.colour: Color = colour
		self.initial = chess.Board()
		self.seen: [str, str] = {}
		self.cards: [str, Page] = {}
		self.last_text = None
		self.accumulated_comments = []
		self.my_move = True

	def visit_move(self, board, move) -> chess.Board:
		if board.turn == self.colour:
			if board.ply():
				saved_piece_symbol = chess.piece_symbol
				chess.piece_symbol = i18n_piece_symbol
				text = self.initial.variation_san(board.move_stack)
				chess.piece_symbol = saved_piece_symbol
			else:
				text = _('Moves from starting position?')
			answer_board = board.copy()
			saved_piece_symbol = chess.piece_symbol
			chess.piece_symbol = i18n_piece_symbol
			san = answer_board.san(move)
			chess.piece_symbol = saved_piece_symbol
			answer_board.push(move)
			fen = answer_board.fen
			if fen in self.seen:
				# Already seen.
				return board

			answer = Answer(
			    san,
			    fullmove_number=board.fullmove_number,
			    turn=board.turn,
			    board=answer_board,
			    colour=self.colour,
			)

			if text not in self.cards:
				turn = not board.turn
				self.cards[text] = Question(
				    text,
				    turn=turn,
				    colour=self.colour,
				)
				if hasattr(self, 'accumulated_comments'):
					for comment in self.accumulated_comments:
						self.cards[text].add_comment(comment)
						self.accumulated_comments = []
				self.cards[text].set_board(board.copy())
			elif answer.find(self.cards[text].answers):
				# Already seen.  Is this redundant?
				return board

			self.cards[text].add_answer(answer)
			self.my_move = True
			self.last_text = text
		else:
			self.accumulated_comments = []
			self.my_move = False

		return board

	def visit_comment(self, comment: str) -> None:
		if self.last_text:
			question = self.cards[self.last_text]
			if self.my_move:
				question.answers[-1].add_comment(comment)
			elif self.accumulated_comments:
				self.accumulated_comments.append(comment)

	def result(self) -> Literal[True]:
		return True

	def print_cards(self) -> None:
		for question in self.cards.values():
			print(f'Q: {question.render()}')
			print('A: Playable moves:')

			print(question.render_answers())
			print()
