# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from io import TextIOWrapper
from typing import Dict, List

import chess
from anki.decks import Deck
from anki.notes import NotetypeDict

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
