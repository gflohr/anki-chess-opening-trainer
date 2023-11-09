from __future__ import annotations

import gettext
import os
import re
import sys
import yaml
import shutil
import hashlib
import typing
from typing import Any, Literal
import chess.pgn
import chess.svg
from chess import Color, Board
from chess.svg import Arrow
from anki.collection import Collection
from anki.notes import Note
from anki.decks import Deck

ARROWS_REGEX = re.compile(r"""
	(?P<prefix>[ \t\n\v\f\r]*?)
	\[%(?P<type>c[as]l)\s(?P<arrows>
		[RGYB]?[a-h][1-8](?:[a-h][1-8])?
		(?:[ \t\n\v\f\r]*,[ \t\n\v\f\r]*[RGYB]?[a-h][1-8](?:[a-h][1-8])?)*
	)\]
	(?P<postfix>[ \t\n\v\f\r]*?)
	""", re.VERBOSE)

WS_REGEX = re.compile('[ \t\n\v\\f]')

# Monkey-patch the piece_symbol() method.
def i18n_piece_symbol(piece: chess.PieceType):
	PIECE_SYMBOLS = [
		None,
		# TRANSLATORS: This is the letter to use for a pawn.
		_('p'),
		# TRANSLATORS: This is the letter to use for a knight.
		_('n'),
		# TRANSLATORS: This is the letter to use for a bishop.
		_('b'),
		# TRANSLATORS: This is the letter to use for a rook.
		_('r'),
		# TRANSLATORS: This is the letter to use for a queen.
		_('q'),
		# TRANSLATORS: This is the letter to use for a king.
		_('k'),
	]
	return typing.cast(str, PIECE_SYMBOLS[piece])

class Page:
	def __init__(self) -> None:
		self.comments: [str] = []
		self.arrows: [Arrow] = []
		self.fills: [int, str] = {}
		self.board: Board | None = None

	def set_board(self, board: Board) -> None:
		self.board = board

	def process_arrows(self, comment: str) -> str:
		def purge_arrows(match):
			type = match.group('type')
			specs = match.group('arrows')
			specs = re.sub(WS_REGEX, '', specs)

			if 'cal' == type:
				for spec in specs.split(','):
					try:
						self.arrows.append(Arrow.from_pgn(re.sub(WS_REGEX, '', spec)))
					except:
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

	def image_path(self) -> str:
		path = ''

		if not self.board:
			self.board = InternationalBoard()
		name = self.board.fen()
		name += '-' + self.object_id()

		for arrow in self.arrows:
			name += '-' + arrow.pgn()
		for square in sorted(self.fills.keys()):
			name += '-' + str(square) + '-' + self.fills[square]
		
		name = hashlib.sha1(name.encode('ascii')).hexdigest() + '.svg'
		path = f'opening-trainer-' + name
		
		return path;

	def extra_html(self) -> str:
		rendered = ''
		for comment in self.comments:
			rendered += ' <em>' + comment + '</em>'

		image_path = self.image_path()
		rendered += f'<br><img src="{image_path}">'
		
		return rendered;

	def render_svg(self, path: str) -> None:
		if self.board.ply():
			lastmove = self.board.peek()
		else:
			lastmove = None
		if (self.board.is_check()):
			check = self.board.king(not self.turn)
		else:
			check = None

		if config['pgn']['csl_is_circle']:
			arrows = self.arrows.copy()

			for square, side in self.fills.items():
				arrows.append(Arrow(tail=square, head=square, color=side))
			svg = chess.svg.board(
				self.board,
				lastmove=lastmove,
				orientation=colour,
				arrows=arrows,
				check=check
			)
		else:
			svg = chess.svg.board(
				self.board,
				lastmove=lastmove,
				orientation=orientation,
				arrows=arrows,
				fill=self.fills,
				check=check
			)

		with open(path, 'w') as file:
			file.write(svg)

class Answer(Page):
	def __init__(self,
			  move: str,
			  fullmove_number: int,
			  turn: Color,
			  board: Board) -> None:
		self.move = move
		self.fullmove_number = fullmove_number
		self.turn = turn
		Page.__init__(self)
		self.set_board(board)

	def render(self) -> str:
		rendered = str(self.fullmove_number) + '.'
		if not self.turn:
			rendered += '...'
		rendered += ' ' + self.move
		rendered += self.extra_html()

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


class Question(Page):
	def __init__(self,
			  moves: str,
			  turn: Color) -> None:
		self.moves = moves
		self.turn = turn
		self.answers: [Answer] = []
		Page.__init__(self)
	
	def add_answer(self, answer: Answer) -> None:
		self.answers.append(answer)

	def render(self) -> str:
		rendered = self.moves
		rendered += self.extra_html()

		return rendered

	def render_answers(self) -> str:
		lines = list(map(Answer.render, self.answers))
		return '<br>'.join(lines)

	def object_id(self) -> str:
		return 'q'

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


class PositionVisitor(chess.pgn.BaseVisitor):
	def visit_move(self, board, move) -> chess.Board:
		if board.turn == colour:
			if board.ply():
				saved_piece_symbol = chess.piece_symbol
				chess.piece_symbol = i18n_piece_symbol
				text = initial.variation_san(board.move_stack)
				chess.piece_symbol = saved_piece_symbol
			else:
				text = _('Moves from starting position?')
			answer_board = board.copy()
			saved_piece_symbol = chess.piece_symbol
			chess.piece_symbol = i18n_piece_symbol
			san = answer_board.san(move)
			chess.piece_symbol = saved_piece_symbol
			answer_board.push(move)
			fen = answer_board.fen
			if fen in seen:
				# Already seen.
				return board

			answer = Answer(
				san,
				fullmove_number = board.fullmove_number,
				turn=board.turn,
				board=answer_board
			)

			if not text in cards:
				turn = not board.turn
				cards[text] = Question(text, turn=turn)
				if hasattr(self, 'accumulated_comments'):
					for comment in self.accumulated_comments:
						cards[text].add_comment(comment)
						self.accumulated_comments = []
				cards[text].set_board(board.copy())
			elif answer.find(cards[text].answers):
				# Already seen.  Is this redundant?
				return board

			cards[text].add_answer(answer)
			self.my_move = True
			self.last_text = text
		else:
			self.accumulated_comments = []
			self.my_move = False

		return board

	def visit_comment(self, comment: str) -> None:
		question = cards[self.last_text]
		if self.my_move:
			question.answers[-1].add_comment(comment)
		elif hasattr(self, 'accumulated_comments'):
			self.accumulated_comments.append(comment)

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


def print_cards(cards: dict[str, Note]) -> None:
	for question in cards.values():
		print(f'Q: {question.render()}')
		print(f'A: Playable moves:')

		print(question.render_answers())
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
		model: Any) -> PatchSet:
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
			card = cards[key]
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

	seen: [str, str] = {}
	cards: [str, Page] = {}
	images: [str, str] = {}
	initial = chess.Board()
	read_study(sys.argv[2])
	print_cards(cards)
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
	patch_set = compute_patch_set(cards, current_notes, model)
	patch_set.patch(col, deck)
