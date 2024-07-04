from typing import List, Sequence

from anki import hooks
from anki.collection import Collection
from anki.notes import NoteId

from .utils import find_media_files

class DeleteHook:


	# pylint: disable=too-few-public-methods
	def installHook(self): # pylint: disable=invalid-name
		def on_notes_delete(collection: Collection, int_note_ids: Sequence[NoteId]):
			mm = collection.media
			media_path = mm.dir()
			note_ids: List[str] = [str(note_id) for note_id in int_note_ids]
			orphans = find_media_files(media_path, note_ids)

			mm.trash_files(orphans)

		hooks.notes_will_be_deleted.append(on_notes_delete)
