# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
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
	def __init__(self, move: str, board: Board, colour: Color):
		fullmove_number = board.fullmove_number
		turn = not board.turn
		self.move = move
		self.fullmove_number = fullmove_number
		Page.__init__(self, colour=colour, turn=turn)
		self.set_board(board)

	def render(self, note_id) -> str:
		rendered = str(self.fullmove_number) + '.'
		if not self.turn:
			rendered += '...'
		rendered += ' ' + self.move
		rendered += self.extra_html(note_id)

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
