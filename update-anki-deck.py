#!/usr/bin/env python

from __future__ import annotations

import gettext
import os
import sys
import yaml
from typing import Any, Literal
import chess.pgn
from chess import Color, Move
from anki.collection import Collection
from anki.notes import Note
from anki.decks import Deck

class Page:
	def __init__(self):
		self.comments: [str] = []

	def addComment(self, comment: str) -> None:
		self.comments.append(comment)


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

		if len(self.comments):
			rendered += ' ' + ' '.join(self.comments)

		return rendered

	def find(self, others: list[Answer]) -> bool:
		for answer in others:
			if (answer.move == self.move
	   		    and answer.fullmove_number == self.fullmove_number
			    and answer.turn == self.turn):
				return True
		
		return False

	@classmethod
	def renderAnswers(cls, answers: list[Answer]) -> str:
		lines = list(map(cls.render, answers))
		return '<br>'.join(lines)


class Question(Page):
	def __init__(self, moves: str) -> None:
		self.moves = moves
		Page.__init__(self)


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
				question = initial.variation_san(board.move_stack)
			else:
				question = gettext.gettext('Moves from starting position?')

			answer = Answer(
				board.san(move),
				fullmove_number = board.fullmove_number,
				turn = board.turn,
			)

			if not question in questions:
				questions[question] = []
			elif answer.find(questions[question]):
				# Already seen
				return board

			questions[question].append(answer)
			self.my_move = True
			self.last_question = question
		else:
			self.my_move = False

		return board

	def visit_comment(self, comment: str) -> None:
		if self.my_move:
			questions[self.last_question][-1].addComment(comment)
		else:
			pass

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


def print_questions(questions: dict[str, Note]) -> None:
	for question, answers in questions.items():
		print(f'Q: {question}')
		print(f'A: Playable moves:')

		print(Answer.renderAnswers(answers))
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
		wanted: dict[str, Answer],
		got: dict[str, Note],
		model: Any) -> PatchSet:
	used: list[str] = []
	inserts: list[Note] = []
	updates: list[Note] = []
	deletes: list[int] = []
	patchSet = PatchSet(inserts, deletes, updates)
	for key, answers in wanted.items():
		answer = Answer.renderAnswers(answers)
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
	questions = {}
	initial = chess.Board()
	read_study(sys.argv[2])
	print_questions(questions)
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
	patch_set = compute_patch_set(questions, current_notes, model)
	patch_set.patch(col, deck)

