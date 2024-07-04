import os
import re
from typing import List, Sequence

from anki import hooks
from anki.collection import Collection
from anki.notes import NoteId

class DeleteHook:


	def installHook(self):
		def on_notes_delete(collection: Collection, int_note_ids: Sequence[NoteId]):
			mm = collection.media
			media_path = mm.dir()
			image_deletes: List[str] = []
			note_ids: List[str] = list(map(lambda note_id: str(note_id), int_note_ids))

			for path in os.scandir(media_path):
				if not os.path.isdir(path.path):
					filename = os.path.basename(path)
					regex = r'^chess-opening-trainer-([1-9][0-9]*)-[0-9a-f]{40}\.svg$'
					match = re.match(regex, filename)
					if not match:
						continue
					note_id = match.group(1)
					if note_id in note_ids:
						image_deletes.append(filename)

			mm.trash_files(image_deletes)

		hooks.notes_will_be_deleted.append(on_notes_delete)
