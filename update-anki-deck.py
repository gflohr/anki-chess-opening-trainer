from __future__ import annotations

import gettext
import os
import re
import sys
import yaml
import shutil
from typing import Any
import chess.pgn
import chess.svg
from chess import Color
from anki.collection import Collection
from anki.notes import Note
from anki.decks import Deck

from page import Page
from question import Question
from visitor import PositionVisitor


class PatchSet():
	def __init__(self,
			  inserts: list[Note],
			  deletes: list[Note],
			  updates: list[Note],
			  image_inserts: [str, Page],
			  image_deletes: [str]
			  ) -> None:
		self.inserts = inserts
		self.deletes = deletes
		self.updates = updates
		self.image_inserts = image_inserts
		self.image_deletes = image_deletes

	def patch(self, col: Collection, deck: Deck):
		deck_id = deck['id']
		for note in self.inserts:
			col.add_note(note=note, deck_id=deck_id)
		for note in self.updates:
			col.update_note(note)

		col.remove_notes(self.deletes)

		for path in self.image_deletes:
			if os.path.isdir(path):
				shutil.rmtree(path, ignore_errors=True)
			else:
				try:
					os.unlink(path)
				except:
					pass
		
		base_path = os.path.join(config['anki']['path'], 'collection.media')
		for image_path, page in self.image_inserts.items():
			path = os.path.join(base_path, image_path)
			page.render_svg(path)


def read_config() -> dict[str, Any]:
	with open('config.yaml', 'r') as file:
		config = yaml.safe_load(file)
		return config


def read_study(filename: str) -> None:
	study_pgn = open(filename)
	def get_visitor() -> chess.pgn.BaseVisitor:
		return visitor

	while chess.pgn.read_game(study_pgn, Visitor=get_visitor):
		pass


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
		model: Any,
	) -> PatchSet:
	used: list[str] = []
	inserts: list[Note] = []
	updates: list[Note] = []
	deletes: list[int] = []
	image_inserts: [str, Page] = {}
	image_deletes: list[str] = []

	media_path = os.path.join(config['anki']['path'], 'collection.media')
	for path in os.scandir(media_path):
		if not os.path.isdir(media_path):
			filename = os.path.basename(path)
			if re.match('^[0-9a-f]{45}\.svg', filename):
				image_deletes.append(path.path)

	patchSet = PatchSet(
		inserts=inserts,
		deletes=deletes,
		updates=updates,
		image_inserts=image_inserts,
		image_deletes=image_deletes)

	for key, question in wanted.items():
		answer = question.render_answers()
		
		# Questions always get a board image.
		image_path = question.image_path()
		if image_path in image_deletes:
			image_deletes.remove(image_path)
		else:
			image_inserts[image_path] = question

		if key in got:
			used.append(key)
			note = got[key]
			if not note.fields[1] == answer:
				note.fields[1] = answer
				updates.append(note)
		else:
			note = Note(col, model)
			card = wanted[key]
			note.fields[0] = card.render()
			note.fields[1] = answer
			inserts.append(note)
		
		for answer in question.answers:
			image_path = answer.image_path()
			if image_path in image_deletes:
				image_deletes.remove(image_path)
			elif image_path:
				image_inserts[image_path] = answer

	for key, note in got.items():
		if not key in used:
			deletes.append(note.id)

	return patchSet


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print(f'Usage: {sys.argv[0]} WHITE|BLACK STUDY_PGN', file=sys.stderr)
		sys.exit(1)

	colour_arg = sys.argv[1].lower()[0]
	if colour_arg == 'w':
		colour = chess.WHITE
	else:
		colour = chess.BLACK

	config = read_config()

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation('opening-trainer', localedir=localedir, languages=[config['locale']])
	t.install()

	visitor = PositionVisitor(colour=colour, csl_is_circle=config['pgn']['csl_is_circle'])
	# FIXME! Read multiple files!
	read_study(sys.argv[2])
	visitor.print_cards()
	col = read_collection(config['anki']['path'])

	notetype = config['anki']['notetype']
	model = col.models.by_name(notetype)
	if not model:
		raise Exception(f"Note type '{notetype}' does not exist")

	if (colour == chess.WHITE):
		deck_name = config['anki']['decks']['white']
	else:
		deck_name = config['anki']['decks']['black']
	
	deck = col.decks.by_name(deck_name)
	if not deck:
		raise Exception(f"Deck '{deck_name}' does not exist")

	current_notes = read_notes(col)
	patch_set = compute_patch_set(visitor.cards, current_notes, model)
	patch_set.patch(col, deck)
