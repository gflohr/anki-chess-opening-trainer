# Copyright (C) 2023 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

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
		self.answers: [Answer] = []
		Page.__init__(self, colour=colour, turn=turn)

	def add_answer(self, answer: Answer) -> None:
		self.answers.append(answer)

	def render(self) -> str:
		rendered = self.moves
		rendered += self.extra_html()

		return rendered

	def render_answers(self) -> str:
		lines = list(map(Answer.render, self.answers))
		return '<br>'.join(lines)

	def object_id(self) -> str:
		return 'q'
