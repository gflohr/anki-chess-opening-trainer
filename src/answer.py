# Copyright (C) 2023-2026 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from __future__ import annotations

from urllib import parse

from chess import Board, Color, STARTING_FEN
from chess.pgn import Game, StringExporter

from .page import Page


class Answer(Page):
	def __init__(self, move: str, board: Board, game: Game, colour: Color, web_path: str):
		fullmove_number = board.fullmove_number
		turn = not board.turn
		self.move = move
		self.fullmove_number = fullmove_number
		Page.__init__(self, colour=colour, turn=turn, web_path=web_path)
		self.set_board(board)
		self.game = game

	def lichess_link(self) -> str | None:
		if self.board is None:
			return None

		# Print the PGN string representation.
		exporter = StringExporter(headers=False, variations=False, comments=False)
		moves = self.game.accept(exporter)

		if self.game.board().fen() == STARTING_FEN:
			headers = ''
		else:
			fen = self.game.board().fen()
			headers = f'[Setup "1"]\n[FEN "{fen}"]\n\n'

		pgn = parse.quote(headers + moves, safe='')

		return f'https://lichess.org/analysis/pgn/{pgn}'

	def extra_html(self, note_id: int) -> str:
		rendered = super().extra_html(note_id)
		link = self.lichess_link()
		if link is not None:
			label = _('Open in Lichess')
			rendered += (
				'<br>'
				f'<a href="{link}" '
				'target="_blank" '
				'rel="noopener noreferrer">'
				f'{label}'
				'</a>'
			)

		return rendered

	def render(self, note_id) -> str:
		rendered = str(self.fullmove_number) + '.'
		if not self.turn:
			rendered += ' ...'
		rendered += ' ' + self.move
		rendered += self.extra_html(note_id)

		return rendered

	def find(self, others: list[Answer]) -> bool:
		for answer in others:
			if (answer.move == self.move
			    and answer.fullmove_number == self.fullmove_number
			    and answer.turn == self.turn):
				return True

		return False

	def object_id(self) -> str:
		return 'a'
