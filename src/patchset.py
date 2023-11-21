import dataclasses
import os
import shutil

from anki.collection import Collection
from anki.decks import Deck
from anki.notes import Note

from .page import Page


@dataclasses.dataclass
class PatchSet:
	inserts: list[Note]
	deletes: list[Note]
	updates: list[Note]
	image_inserts: [str, Page]
	image_deletes: [str]
	media_path: str


def patch(ps: PatchSet, col: Collection,
          deck: Deck) -> [int, int, int, int, int]:
	deck_id = deck['id']
	for note in ps.inserts:
		col.add_note(note=note, deck_id=deck_id)
	for note in ps.updates:
		col.update_note(note)

	col.remove_notes(ps.deletes)

	for filename in ps.image_deletes:
		path = os.path.join(ps.media_path, filename)
		if os.path.isdir(path):
			shutil.rmtree(path, ignore_errors=True)
		else:
			try:
				os.unlink(path)
			except OSError:
				pass

	for image_path, page in ps.image_inserts.items():
		path = os.path.join(ps.media_path, image_path)
		page.render_svg(path)

	return [
	    len(ps.inserts),
	    len(ps.updates),
	    len(ps.deletes),
	    len(ps.image_inserts),
	    len(ps.image_deletes),
	]
