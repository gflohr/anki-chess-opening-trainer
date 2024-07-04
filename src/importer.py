# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, cast

import chess
from anki.collection import Collection
from anki.notes import Note, NoteId, NotetypeId
from anki.decks import DeckId

from .answer import Answer
from .question import Question
from .page import Page
from .visitor import PositionVisitor


class Importer:


	# pylint: disable=too-many-arguments, too-few-public-methods
	def __init__(
	    self,
	    filenames: List[str],
	    collection: Collection,
	    colour: chess.Color,
	    notetype_id: NotetypeId,
	    deck_id: DeckId
	) -> None:
		self.collection = collection
		self.colour = colour

		model_data = self.collection.models.get(notetype_id)
		if model_data is None:
			raise KeyError(_('Selected note type does not exist!'))
		self.model = model_data

		deck_data: Optional[Dict[str, Any]] = self.collection.decks.get(did=deck_id)
		if deck_data is None:
			raise KeyError(_('Selected deck does not exist!'))
		self.deck = deck_data

		self.visitor = PositionVisitor(colour=colour)
		self.filenames = filenames


	def run(self) -> Tuple[int, int, int, int, int]:
		for filename in self.filenames:
			self._read_study(filename)
		current_notes = self._read_notes()

		return self._patch_deck(current_notes)

	def _read_study(self, filename: str) -> None:
		with open(filename, encoding='utf-8') as study_pgn:

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
			# Remove all the markup from the end.  It is actually a br followed
			# by an img.  Questions do not have comments.
			name = re.sub('[ \t\r\n]*<.*', '', note.fields[0])
			notes[name] = note

		return notes

	def _delete_unused(self,  wanted: Dict[str, Question], got: dict[str, Note]) -> int:
		deletes: List[NoteId] = []
		for moves in got:
			if moves not in wanted:
				note = got[moves]
				deletes.append(note.id)
		deletes_sequence: Sequence = cast(Sequence, deletes)
		self.collection.remove_notes(deletes_sequence)

		return len(deletes_sequence)

	def _images_in_deck(self, got: dict[str, Note]) -> List[str]:
		# Initialize image_deletes with all images we find for this deck.
		image_deletes: List[str] = []
		media_path = self.collection.media.dir()
		note_ids = list(map(lambda moves: str(got[moves].id), got))
		for path in os.scandir(media_path):
			if not os.path.isdir(path.path):
				filename = os.path.basename(path)
				regex = r'^chess-opening-trainer-([1-9][0-9]*)-[0-9a-f]{40}\.svg$'
				match = re.match(regex, filename)
				if not match:
					continue
				note_id = match.group(1)
				if note_id in note_ids:
					image_deletes.append(filename)

		return image_deletes

	def _update_note(self, note: Note, question: Question) -> bool:
		rendered_question = question.render(note.id)
		answer: Answer = cast(Answer, question.render_answers(note.id))
		if not note.fields[0] == rendered_question or not note.fields[1] == answer:
			note.fields[0] = rendered_question
			note.fields[1] = answer
			self.collection.update_note(note)
			return True

		return False

	def _create_note(self, question: Question) -> Note:
		note = Note(self.collection, self.model)

		# We have to add the note first without content so that we have a
		# note id to work with.
		self.collection.add_note(note, deck_id=self.deck['id'])
		note.fields[0] = question.render(note.id)
		answer: Answer = cast(Answer, question.render_answers(note.id))
		note.fields[1] = answer
		self.collection.update_note(note)

		return note

	def _insert_images(self, image_inserts: Dict[str, Page]):
		media_path = self.collection.media.dir()
		for image_path, page in image_inserts.items():
			path = os.path.join(media_path, image_path)
			page.render_svg(path)

	def _patch_deck(self, got: dict[str, Note]) -> Tuple[int, int, int, int, int]:
		# These are the cards that we want to have from the current studies
		# that were read.
		wanted = self.visitor.cards

		# Initialize the images to delete with a list of all images for the
		# current notes.
		image_deletes = self._images_in_deck(got)

		num_deletes = self._delete_unused(wanted, got)

		image_inserts: Dict[str, Page] = {}

		num_updates = 0
		num_inserts = 0
		for moves, question in wanted.items():

			if moves in got:
				# There is a note for it but maybe it has changed.
				note = got[moves]
				if self._update_note(note, question):
					num_updates = num_updates + 1
			else:
				# The note must be created.
				note = self._create_note(question)
				num_inserts = num_inserts + 1

			# Questions always get a board image.
			image_path = question.image_path(note.id)
			if image_path in image_deletes:
				image_deletes.remove(image_path)
			else:
				image_inserts[image_path] = question

			for answer in question.answers:
				image_path = answer.image_path(note.id)
				if image_path in image_deletes:
					image_deletes.remove(image_path)
				elif image_path:
					image_inserts[image_path] = answer

		self._insert_images(image_inserts)
		self.collection.media.trash_files(image_deletes)

		num_image_deletes = len(image_deletes)
		num_image_inserts = len(image_inserts)

		return num_inserts, num_updates, num_deletes, num_image_inserts, num_image_deletes
