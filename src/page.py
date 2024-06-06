# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import hashlib
import re
from typing import Dict, List, Optional

import chess
from chess import Board
from chess.svg import Arrow

ARROWS_REGEX = re.compile(
    r"""
	(?P<prefix>[ \t\n\v\f\r]*?)
	\[%(?P<type>c[as]l)\s(?P<arrows>
		[RGYB]?[a-h][1-8](?:[a-h][1-8])?
		(?:[ \t\n\v\f\r]*,[ \t\n\v\f\r]*[RGYB]?[a-h][1-8](?:[a-h][1-8])?)*
	)\]
	(?P<postfix>[ \t\n\v\f\r]*?)
	""", re.VERBOSE)

WS_REGEX = re.compile('[ \t\n\v\\f]')


class Page:
	def __init__(self, colour: chess.Color, turn: chess.Color) -> None:
		self.colour = colour
		self.turn = turn
		self.comments: List[str] = []
		self.arrows: List[Arrow] = []
		self.fills: Dict[int, str] = {}
		self.board: Optional[Board] = None

	def set_board(self, board: Board) -> None:
		self.board = board

	def process_arrows(self, comment: str) -> str:
		def purge_arrows(match):
			arrow_type = match.group('type')
			specs = match.group('arrows')
			specs = re.sub(WS_REGEX, '', specs)

			if 'cal' == arrow_type:
				for spec in specs.split(','):
					try:
						self.arrows.append(
						    Arrow.from_pgn(re.sub(WS_REGEX, '', spec)))
					except ValueError:
						# Ignore!
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

	def image_path(self, note_id: int) -> str:
		path = ''

		if not self.board:
			self.board = Board()
		name = self.board.fen() + '-' + self.object_id()

		for arrow in self.arrows:
			name += '-' + arrow.pgn()
		for square in sorted(self.fills.keys()):
			name += '-' + str(square) + '-' + self.fills[square]

		name = hashlib.sha1(name.encode('ascii')).hexdigest() + '.svg'
		path = f'chess-opening-trainer-{note_id}-{name}'

		return path

	def extra_html(self, note_id: int) -> str:
		rendered = ''
		for comment in self.comments:
			rendered += ' <em>' + comment + '</em>'

		image_path = self.image_path(note_id)
		rendered += f'<br><img src="{image_path}">'

		return rendered

	def render_svg(self, path: str) -> None:
		if self.board is None:
			return

		if self.board.ply():
			lastmove = self.board.peek()
		else:
			lastmove = None
		if self.board.is_check():
			check = self.board.king(not self.turn)
		else:
			check = None

		arrows = self.arrows.copy()

		for square, side in self.fills.items():
			arrows.append(Arrow(tail=square, head=square, color=side))
		svg = chess.svg.board(self.board,
		                      lastmove=lastmove,
		                      orientation=self.colour,
		                      arrows=arrows,
		                      check=check)

		with open(path, 'w', encoding='cp1252') as file:
			file.write(svg)

	def object_id(self):
		raise NotImplementedError('method object_id() not implemented')
