from typing import List
from anki.cards import Card
from anki.models import NotetypeDict


_field_names = ['Moves', 'Responses', 'Line', 'FEN']

class ChessNote
	def __init__(self, card: Card):
		self.note = card.note()
		self.is_v1 = False

		notetype = self.note.note_type()
		col = self.note.col
		note_field_names = col.models.field_names(notetype)

		field_map = col.models.field_map(notetype)
		for name in _field_names:
			if name not in note_field_names:
				self.is_v1 = True
				break

		if self.is_v1:
			real_field_map = field_map
			field_map.clear()

			for name, t in real_field_map.items():
				if t[0] == 0:
					field_map['Moves'] = t
				elif t[0] == 1:
					field_map['Responses'] = t


	@classmethod
	def field_names(cls) -> List[str]:
		return _field_names

