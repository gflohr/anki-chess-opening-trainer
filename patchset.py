import shutil
import os

from anki.collection import Collection
from anki.notes import Note
from anki.decks import Deck

from page import Page

class PatchSet():
	def __init__(self,
			inserts: list[Note],
			deletes: list[Note],
			updates: list[Note],
			image_inserts: [str, Page],
			image_deletes: [str],
			media_path: str,
		) -> None:
		self.inserts = inserts
		self.deletes = deletes
		self.updates = updates
		self.image_inserts = image_inserts
		self.image_deletes = image_deletes
		self.media_path = media_path

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
		
		for image_path, page in self.image_inserts.items():
			path = os.path.join(self.media_path, image_path)
			page.render_svg(path)
