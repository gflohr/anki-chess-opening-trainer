from chess import Color

from page import Page
from answer import Answer

class Question(Page):
	def __init__(self,
			  moves: str,
			  turn: Color,
			  colour: Color,
			  csl_is_circle: bool) -> None:
		self.moves = moves
		self.turn = turn
		self.answers: [Answer] = []
		Page.__init__(self, colour=colour, csl_is_circle=csl_is_circle)
	
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
