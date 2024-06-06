# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from typing import List
from chess import Color

from .answer import Answer
from .page import Page


class Question(Page):


	def __init__(
	    self,
	    moves: str,
	    turn: Color,
	    colour: Color,
	) -> None:
		self.moves = moves
		self.answers: List[Answer] = []
		Page.__init__(self, colour=colour, turn=turn)

	def add_answer(self, answer: Answer) -> None:
		self.answers.append(answer)

	def render(self, note_id: int) -> str:
		rendered = self.moves
		rendered += self.extra_html(note_id)

		return rendered

	def render_answers(self, note_id: int) -> str:
		lines: List[str] = []

		for answer in self.answers:
			lines.append(answer.render(note_id))

		return '<br>'.join(lines)

	def object_id(self) -> str:
		return 'q'
