#!/usr/bin/env python

import gettext
import sys
import chess.pgn
import yaml

class PositionVisitor(chess.pgn.BaseVisitor):
	def visit_move(self, board, move) -> chess.Board:
		if board.turn == colour:
			if board.ply():
				question = initial.variation_san(board.move_stack)
			else:
				question = gettext.gettext('Moves from starting position?')
			if not question in questions:
				questions[question] = []
			questions[question].append({
				'move': board.san(move),
				'fullmove_number': board.fullmove_number,
				'turn': board.turn,
			})
			self.my_move = True
			self.last_question = question
		else:
			self.my_move = False

		return board

	def visit_comment(self, comment: str) -> None:
		if self.my_move:
			questions[self.last_question][-1]['comment'] = comment

	def result(self):
		return True


def read_config():
	with open('config.yaml', 'r') as file:
		config = yaml.safe_load(file)
		return config


def read_study(filename):
	study_pgn = open(filename)
	while chess.pgn.read_game(study_pgn, Visitor=PositionVisitor):
		pass


def print_questions(questions):
	for note in questions.items():
		question = note[0]
		print(f'Q: {question}')
		print(f'A: Playable moves:')

		for move in note[1]:
			answer = str(move['fullmove_number']) + '.'
			if not move['turn']:
				answer += ' ...'
			answer += ' ' + move['move']
			if 'comment' in move:
				answer += ' <em>' + move['comment'] + '</em>'
			print(f'- {answer}')
			print()

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} WHITE|BLACK STUDY_PGN', file=sys.stderr)
		sys.exit(1)

	colour_arg = sys.argv[1].lower()[0]

	match colour_arg:
		case 'w':
			colour = chess.WHITE
		case 'b':
			colour = chess.BLACK
		case 's':
			colour = chess.BLACK
		case _:
			print(f'Invalid colour "{sys.argv[1]}".')
			sys.exit(1)

	config = read_config()
	questions = {}
	initial = chess.Board()
	read_study(sys.argv[2])
	print_questions(questions)


