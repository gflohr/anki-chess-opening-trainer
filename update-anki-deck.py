#!/usr/bin/env python

from __future__ import annotations

import gettext
import os
import re
import sys
import yaml
from typing import Any, Literal
import chess.pgn
from chess import Color
from chess.svg import Arrow
from anki.collection import Collection
from anki.notes import Note
from anki.decks import Deck

ARROWS_REGEX = re.compile(r"""
	(?P<prefix>[ \t\n\v\f\r]*?)
	\[%(?P<type>c[as]l)\s(?P<arrows>
		[RGYB]?[a-h][1-8](?:[a-h][1-8])?
		(?:[ \t\n\v\f\r]*,[ \t\n\v\f\r]*[RGYB]?[a-h][1-8](?:[a-h][1-8])?)*
	)\]
	(?P<postfix>[ \t\n\v\f\r]*?)
	""", re.VERBOSE)

WS_REGEX = re.compile('[ \t\n\v\\f]')

class Page:
	def __init__(self) -> None:
		self.comments: [str] = []
		self.arrows: [Arrow] = []
		self.fills: [int, str] = {}

	def process_arrows(self, comment: str) -> str:
		def purge_arrows(match):
			type = match.group('type')
			specs = match.group('arrows')
			specs = re.sub(WS_REGEX, '', specs)

			if 'cal' == type:
				for spec in specs.split(','):
					try:
						self.arrows.append(Arrow.from_pgn(re.sub(WS_REGEX, '', spec)))
					except:
						pass
			else:
				for spec in specs.split(','):
					# %csl takes just a square.  Ignore the rest of the string
					# if two squares had been given.
					colors = {
						'R': 'red',
						'G': 'green',
						'Y': 'yellow',
						'B': 'blue'
					}
					color = 'green'
					if spec[0] in colors:
						color = colors[spec[0]]
						square = chess.parse_square(spec[1:])
					else:
						square = chess.parse_square(spec)

					self.fills[square] = color

			return ''

		return re.sub(ARROWS_REGEX, purge_arrows, comment)

	def add_comment(self, comment: str) -> None:
		comment = self.process_arrows(comment)
		if not re.match('^[ \t\n\v\\f]*$', comment):
			self.comments.append(comment)

	def need_board_image(self) -> bool:
		return False

class Answer(Page):
	def __init__(self,
			  move: str,
			  fullmove_number: int,
			  turn: Color) -> None:
		self.move = move
		self.fullmove_number = fullmove_number
		self.turn = turn
		Page.__init__(self)

	def render(self) -> str:
		rendered = str(self.fullmove_number) + '.'
		if not self.turn:
			answer += '...'
		rendered += ' ' + self.move

		for comment in self.comments:
			rendered += ' ' + comment

		return rendered

	def find(self, others: list[Answer]) -> bool:
		for answer in others:
			if (answer.move == self.move
	   		    and answer.fullmove_number == self.fullmove_number
			    and answer.turn == self.turn):
				return True
		
		return False

	def need_board_image(self) -> bool:
		return len(self.arrows) or len(self.fills)


class Question(Page):
	def __init__(self, moves: str) -> None:
		self.moves = moves
		self.answers: [Answer] = []
		Page.__init__(self)
	
	def add_answer(self, answer: Answer) -> None:
		self.answers.append(answer)

	def render(self) -> str:
		rendered = self.moves

		for comment in self.comments:
			rendered += ' ' + comment

		return rendered

	def render_answers(self) -> str:
		lines = list(map(Answer.render, self.answers))
		return '<br>'.join(lines)

class PatchSet():
	def __init__(self,
			  inserts: list[Note],
			  deletes: list[Note],
			  updates: list[Note],
			  ) -> None:
		self.inserts = inserts
		self.deletes = deletes
		self.updates = updates

	def patch(self, col: Collection, deck: Deck):
		deck_id = deck['id']
		for note in self.inserts:
			col.add_note(note=note, deck_id=deck_id)
		for note in self.updates:
			col.update_note(note)

		col.remove_notes(self.deletes)


class PositionVisitor(chess.pgn.BaseVisitor):
	def visit_move(self, board, move) -> chess.Board:
		if board.turn == colour:
			if board.ply():
				card = initial.variation_san(board.move_stack)
			else:
				card = gettext.gettext('Moves from starting position?')

			answer = Answer(
				board.san(move),
				fullmove_number = board.fullmove_number,
				turn = board.turn,
			)

			if not card in cards:
				cards[card] = Question(card)
				if hasattr(self, 'accumulated_comments'):
					for comment in self.accumulated_comments:
						cards[card].add_comment(comment)
						self.accumulated_comments = []
			elif answer.find(cards[card].answers):
				# Already seen
				return board

			cards[card].add_answer(answer)
			self.my_move = True
			self.last_card = card
		else:
			self.accumulated_comments = []
			self.my_move = False

		return board

	def visit_comment(self, comment: str) -> None:
		question = cards[self.last_card]
		if self.my_move:
			question.answers[-1].add_comment(comment)
		elif hasattr(self, 'accumulated_comments'):
			self.accumulated_comments.append(comment)

	def result(self) -> Literal[True]:
		return True


def read_config() -> dict[str, Any]:
	with open('config.yaml', 'r') as file:
		config = yaml.safe_load(file)
		return config


def read_study(filename: str) -> None:
	study_pgn = open(filename)
	while chess.pgn.read_game(study_pgn, Visitor=PositionVisitor):
		pass


def print_cards(cards: dict[str, Note]) -> None:
	for question in cards.values():
		print(f'Q: {question.render()}')
		print(f'A: Playable moves:')

		print(question.render_answers())
		print()


def read_collection(dir: str) -> Collection:
	collection_path = os.path.join(dir, 'collection.anki2')
	if not os.path.exists(collection_path):
		raise Exception(f"Collection '{collection_path}' does not exist")

	return Collection(collection_path)

def read_notes(col: Collection) -> dict[str, Note]:
	notetype = config['anki']['notetype']
	model = col.models.by_name(notetype)
	if not model:
		raise Exception(f"Note type '{notetype}' does not exist")
	deck_name = config['anki']['deck']
	deck = col.decks.by_name(deck_name)
	if not deck:
		raise Exception(f"Deck '{deck_name}' does not exist")
	deck_id = deck['id']

	notes = {}
	for cid in col.decks.cids(deck_id):
		card = col.get_card(cid)
		note = card.note()
		name = note.fields[0]
		notes[name] = note

	return notes

def compute_patch_set(
		wanted: dict[str, Question],
		got: dict[str, Note],
		model: Any) -> PatchSet:
	used: list[str] = []
	inserts: list[Note] = []
	updates: list[Note] = []
	deletes: list[int] = []
	patchSet = PatchSet(inserts, deletes, updates)
	for key, question in wanted.items():
		answer = question.render_answers()
		if key in got:
			used.append(key)
			note = got[key]
			if not note.fields[1] == answer:
				note.fields[1] = answer
				updates.append(note)

		else:
			note = Note(col, model)
			note.fields[0] = key
			note.fields[1] = answer
			inserts.append(note)

	for key, note in got.items():
		if not key in used:
			deletes.append(note.id)

	return patchSet


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
	cards = {}
	images = {}
	initial = chess.Board()
	read_study(sys.argv[2])
	print_cards(cards)
	col = read_collection(config['anki']['path'])

	notetype = config['anki']['notetype']
	model = col.models.by_name(notetype)
	if not model:
		raise Exception(f"Note type '{notetype}' does not exist")

	deck_name = config['anki']['deck']
	deck = col.decks.by_name(deck_name)
	if not deck:
		raise Exception(f"Deck '{deck_name}' does not exist")

	current_notes = read_notes(col)
	patch_set = compute_patch_set(cards, current_notes, model)
	patch_set.patch(col, deck)

