# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import re
from typing import Dict, List, Sequence, Tuple, cast

import chess
from anki.collection import Collection
from anki.notes import Note, NoteId
from anki.decks import Deck

from .answer import Answer
from .question import Question
from .page import Page
from .patchset import PatchSet, patch
from .visitor import PositionVisitor


class Importer:
	# pylint: disable=too-many-arguments, too-few-public-methods
	def __init__(
	    self,
	    filenames: List[str],
	    collection: Collection,
	    colour: chess.Color,
	    notetype: str,
	    deck_name: str,
	    do_print: bool = False,
	) -> None:
		self.collection = collection
		self.colour = colour

		self.model = self.collection.models.by_name(notetype)
		if not self.model:
			raise KeyError(f"Note type '{notetype}' does not exist")

		self.deck = cast(Deck, collection.decks.by_name(deck_name))
		if not self.deck:
			raise KeyError(f"Deck '{deck_name}' does not exist")

		self.visitor = PositionVisitor(colour=colour)
		self.filenames = filenames

		self.do_print = do_print

	def run(self) -> Tuple[int, int, int, int, int]:
		for filename in self.filenames:
			self._read_study(filename)
		if self.do_print:
			self.visitor.print_cards()
		current_notes = self._read_notes()
		ps = self._compute_patch_set(current_notes)
		return patch(ps, self.collection, self.deck)

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
			name = re.sub('[ \t\r\n]*<.*', '', note.fields[0])
			notes[name] = note

		return notes

	def _compute_patch_set(self, got: dict[str, Note]) -> PatchSet:
		# FIXME! Use the PatchSet that gets returned here.
		# pylint: disable=too-many-locals, too-many-branches
		used: List[str] = []
		inserts: List[Note] = []
		updates: List[Note] = []
		deletes: List[NoteId] = []
		image_inserts: Dict[str, Page] = {}
		image_deletes: List[str] = []
		media_path = self.collection.media.dir()

		wanted = self.visitor.cards
		model = self.model
		if self.colour:
			colour = 'w'
		else:
			colour = 'b'
		for path in os.scandir(media_path):
			if not os.path.isdir(path.path):
				filename = os.path.basename(path)
				prefix = '^chess-opening-trainer-' + colour
				regex = prefix + r'-[0-9a-f]{40}\.svg'
				if re.match(regex, filename):
					image_deletes.append(filename)

		for key, q in wanted.items():
			question: Question = cast(Question, q)
			answer: Answer = cast(Answer, question.render_answers())

			# Questions always get a board image.
			image_path = question.image_path()
			if image_path in image_deletes:
				image_deletes.remove(image_path)
			else:
				image_inserts[image_path] = question

			q2: Question = cast(Question, wanted[key])
			rendered_question: Question = cast(Question, q2.render())
			if key in got:
				used.append(key)
				note = got[key]
				if not note.fields[0] == rendered_question or not note.fields[
				    1] == answer:
					note.fields[0] = rendered_question
					note.fields[1] = answer
					updates.append(note)
			else:
				note = Note(self.collection, model)
				note.fields[0] = rendered_question
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

		deletes_sequence: Sequence = cast(Sequence, deletes)

		return PatchSet(inserts=inserts,
		                deletes=deletes_sequence,
		                updates=updates,
		                image_inserts=image_inserts,
		                image_deletes=image_deletes,
		                media_path=media_path)
