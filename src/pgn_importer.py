# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from io import TextIOWrapper
from typing import Dict, List, Tuple, Union

import chess

from aqt import mw
from anki.decks import Deck
from anki.notes import Note, NotetypeDict, NoteId
from anki.cards import Card, CardId

from .position_visitor import PositionVisitor
from .chess_line import ChessLine
from .game_node import GameNode


class ChangeRecord:
	def __init__(self, card: Union[Card, None], line: Union[ChessLine, None]):
		self._card = card
		self._line = line

	@property
	def card(self):
		return self._card

	@property
	def line(self):
		return self._line


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
				pass

		cards = self.get_cards()
		lines = self.get_lines()

		inserts, updates, deletes = self._analyze_deck(cards, lines)

		self.import_records(inserts)

		return len(inserts), len(updates), len(deletes)

	def _analyze_deck(self, cards: Dict[str, Card], lines: List[ChessLine]) -> Tuple[List[ChangeRecord], List[ChangeRecord], List[ChangeRecord]]:
		updates: List[ChangeRecord] = []
		deletes: List[ChangeRecord] = []

		lines_by_signature = { line.signature() : line for line in lines }

		line_index = self._field_index('Line')
		for csignature, card in cards.items():
			if csignature in lines_by_signature:
				line = lines_by_signature[csignature]
				pgn_line_json = lines_by_signature[csignature].to_json()
				del lines_by_signature[csignature]
				note = card.note()
				card_line_json = note.fields[line_index]
				if pgn_line_json != card_line_json:
					updates.append(ChangeRecord(card, line))
			else:
				deletes.append(ChangeRecord(card, None))

		inserts = [ChangeRecord(None, line) for line in lines_by_signature.values()]

		return inserts, updates, deletes

	def collect(self, file: TextIOWrapper):
		def get_visitor() -> PositionVisitor:
			return self.visitor

		while chess.pgn.read_game(file, Visitor=get_visitor):
			pass

	def get_lines(self) -> List[ChessLine]:
		nodes = self._merge(self.visitor.nodes)
		game_comments = self.visitor.game_comments

		self._clean_nags(nodes)

		nodes_by_signature = {node.signature(): node for node in nodes}

		colour = chess.BLACK if self.colour == 'black' else chess.WHITE

		lines: List[ChessLine] = []
		for node in nodes:
			if node.colour != colour:
				line_nodes: List[GameNode] = []
				previous_signatures = node.previous_signatures()
				for signature in previous_signatures:
					line_nodes.append(nodes_by_signature[signature])
				line_nodes.append(node)
				lines.append(ChessLine(line_nodes, game_comments))

		return lines

	def import_records(self, records: List[ChangeRecord]) -> List[NoteId]:
		for record in records:
			line = record.line
			if line.turn == self.colour:
				self._insert_line(line)

	def _insert_line(self, line: ChessLine):
		note = Note(mw.col, self.model)
		self.fill_note(note, line)
		#mw.col.add_note(note, deck_id=self.deck['id'])

	def get_cards(self) -> Dict[str, Card]:
		collection = mw.col
		line_index = self._field_index('Line')

		cards: Dict[str, Card] = {}
		for cid in collection.decks.cids(self.deck['id']):
			card = collection.get_card(cid)
			note = card.note()
			if note.note_type['id'] == self.model['id']:
				signature = ChessLine.signature_from_json(note.fields[line_index])
				if signature is not None:
					cards[signature] = card

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

		return list(merged.values())

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

	def fill_note(self, note: Note, line: ChessLine):
		fields = note.fields

		moves_index = self._field_index('Moves')
		fields[moves_index] = line.render_question()

		responses_index = self._field_index('Responses')
		fields[responses_index] = line.render_answer()

		line_index = self._field_index('Line')
		fields[line_index] = line.to_json()

	def _field_index(
			self,
			name: str,
		) -> int:
		model = self.model
		field_map = mw.col.models.field_map(model)
		if not name in field_map:
			raise KeyError(_("Note type '{type}' lacks field '{name}'!").format(
				type=model['name'], name=name
			))
		return field_map[name][0]

