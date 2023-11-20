import os
import re
import chess
from typing import Any
from anki.collection import Collection
from anki.notes import Note
from patchset import PatchSet

from visitor import PositionVisitor
from page import Page

class Importer:
	def __init__(self,
		filenames: [str],
		collection: Collection,
		colour: chess.Color,
		notetype: str,
		deck_name: str,
		doPrint: bool=False,
	) -> None:
		self.collection = collection
		self.colour = colour

		self.model = self.collection.models.by_name(notetype)
		if not self.model:
			raise Exception(f"Note type '{notetype}' does not exist")

		self.deck = collection.decks.by_name(deck_name)
		if not self.deck:
			raise Exception(f"Deck '{deck_name}' does not exist")

		self.visitor = PositionVisitor(colour=colour)
		self.filenames = filenames

		self.doPrint = print

	def run(self) -> [int, int, int]:
		for filename in self.filenames:
			self._read_study(filename)
		if self.doPrint:
			self.visitor.print_cards()
		current_notes = self._read_notes()
		patch_set = self._compute_patch_set(current_notes)
		return patch_set.patch(self.collection, self.deck)

	def _read_study(self, filename: str) -> None:
		# The encoding "cp1252" is pretty much equivalent to binary.  It also
		# covers the range from 128 to 159 avoiding encoding errors.  And
		# we just pass through characters to Anki and therefore don't care
		# about character semantics.
		study_pgn = open(filename, encoding='cp1252')
		def get_visitor() -> chess.pgn.BaseVisitor:
			return self.visitor

		while chess.pgn.read_game(study_pgn, Visitor=get_visitor):
			pass

	def _read_notes(self) -> dict[str, Note]:
		col = self.collection
		deck_id = self.deck['id']

		notes = {}
		for cid in col.decks.cids(deck_id):
			card = col.get_card(cid)
			note = card.note()
			name = re.sub('[ \t\r\n]*<.*', '', note.fields[0])
			notes[name] = note

		return notes

	def _compute_patch_set(self, got: dict[str, Note]) -> PatchSet:
		used: list[str] = []
		inserts: list[Note] = []
		updates: list[Note] = []
		deletes: list[int] = []
		image_inserts: [str, Page] = {}
		image_deletes: list[str] = []

		wanted = self.visitor.cards
		model = self.model
		media_path = self.collection.media.dir()
		for path in os.scandir(media_path):
			if not os.path.isdir(path.path):
				filename = os.path.basename(path)
				if re.match('^chess-opening-trainer-[0-9a-f]{40}\.svg', filename):
					image_deletes.append(filename)

		patchSet = PatchSet(
			inserts=inserts,
			deletes=deletes,
			updates=updates,
			image_inserts=image_inserts,
			image_deletes=image_deletes,
			media_path=media_path)

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
				note = Note(self.collection, model)
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
