# Copyright (C) 2023 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from __future__ import annotations

from chess import Board, Color

from .page import Page


class Answer(Page):
	# FIXME! Try to get rid of the arguments fullmove_number and turn and
	# derive them from the board instead.
	# pylint: disable=too-many-arguments
	def __init__(self, move: str, fullmove_number: int, turn: Color,
	             board: Board, colour: Color) -> None:
		self.move = move
		self.fullmove_number = fullmove_number
		Page.__init__(self, colour=colour, turn=turn)
		self.set_board(board)

	def render(self) -> str:
		rendered = str(self.fullmove_number) + '.'
		if not self.turn:
			rendered += '...'
		rendered += ' ' + self.move
		rendered += self.extra_html()

		return rendered

	def find(self, others: list[Answer]) -> bool:
		for answer in others:
			if (answer.move == self.move
			    and answer.fullmove_number == self.fullmove_number
			    and answer.turn == self.turn):
				return True

		return False

	def object_id(self) -> str:
		return 'a'
