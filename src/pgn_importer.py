# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from io import TextIOWrapper
from typing import Dict, List, Tuple, cast

import chess

from aqt import mw
from anki.decks import Deck
from anki.notes import Note, NotetypeDict, NoteId
from anki.cards import CardId
from anki.models import FieldDict

from .position_visitor import PositionVisitor
from .line import Line
from .game_node import GameNode


class PGNImporter:

	def __init__(
	    self,
	    colour: chess.Color,
	    model: NotetypeDict,
	    deck: Deck
	) -> None:
		self.colour = colour
		self.model = model
		self.deck = deck
		self.visitor = PositionVisitor()

	def run(self, filenames: List[str]) -> Tuple[int, int, int, int, int]:
		for filename in filenames:
			try:
				with open(filename, 'r') as file:
					self.collect(file)
			except Exception as e:
				# File was deleted, corrupt, whatever.
				pass

		lines = self.get_lines()

		self.import_lines(lines)

		return 1, 2, 3, 4, 5

	def collect(self, file: TextIOWrapper):
		def get_visitor() -> PositionVisitor:
			return self.visitor

		while chess.pgn.read_game(file, Visitor=get_visitor):
			pass

	def get_lines(self) -> List[Line]:
		nodes = self._merge(self.visitor.get_nodes())
		self._clean_nags(nodes)

		nodes_by_signature = {node.signature(): node for node in nodes}

		colour = chess.BLACK if self.colour == 'black' else chess.WHITE

		lines: List[Line] = []
		for node in [x for x in nodes if x.colour == colour]:
			line_nodes: List[GameNode] = []
			previous_signatures = node.previous_signatures()
			for signature in previous_signatures:
				line_nodes.append(nodes_by_signature[signature])
			line_nodes.append(node)
			lines.append(Line(line_nodes))

		return lines

	def import_lines(self, lines: List[Line]) -> Tuple[List[NoteId], List[NoteId]]:
		new_lines = lines.copy()

		inserted = self._insert_lines(new_lines)

	def _insert_lines(self, lines: List[Line]) -> List[NoteId]:
		inserted: List[NoteId] = []

		for line in lines:
			inserted.append(self._insert_line(line))
			self._insert_line(line)

		return inserted

	def _insert_line(self, line: Line) -> NoteId:
		note = Note(mw.col, self.model)
		self.fill_note(note, line)

		print(note)

		return note.id

	def get_cards(self) -> Dict[str, CardId]:
		collection = mw.col

		cards: Dict[str, CardId] = []
		for cid in collection.decks.cids():
			card = collection.get_card(cid)
			note = card.note()
			cards[cid] = note.fields[0]
		return cards

	def _merge(self, nodes: List[GameNode]) -> List[GameNode]:
		merged: Dict[str, GameNode] = {}
		for node in nodes:
			signature = node.signature()
			if signature in merged:
				first = merged[signature]
				first.merge(node)
			else:
				merged[signature] = node

		return merged.values()

	def _clean_nags(self, nodes: List[GameNode]):
		# Unfortunately, Python chess only supports the six basic NAGs.
		# While it is theoretically possible that a move is annotated with
		# multiple NAGs, it does not make sense.  Therefore, we merge all
		# NAGs of a move into maximum one.  If all of them are identical,
		# we use this one.  Otherwise, if they are not identical, we just
		# delete them because we cannot decide which one is right.
		for node in nodes:
			nags = node.nags
			if len(nags) and all(nag == nags[0] for nag in nags):
				node.nags = [nags[0]]
			else:
				node.nags = []

	def fill_note(self, note: Note, line: Line):
		model = cast(NotetypeDict, note.note_type())
		moves_index = self._field_index('Moves', model)
		fields = note.fields
		fields[moves_index] = line.nodes[-1].signature_v1()

		print(f'fields: {fields}')

	def _field_index(
			self,
			name: str,
			model: NotetypeDict,
		) -> int:

		field_map = mw.col.models.field_map(model)
		if not name in field_map:
			raise KeyError(_("Note type '{type}' lacks field '{name}'!").format(
				type=model['name'], name=name
			))
		return field_map[name][0]

