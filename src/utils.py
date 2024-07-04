import os
import re
from typing import List


def find_media_files(media_path: str, note_ids: list[str]):
	filenames: List[str] = []

	for path in os.scandir(media_path):
		if not os.path.isdir(path.path):
			filename = os.path.basename(path)
			regex = r'^chess-opening-trainer-([1-9][0-9]*)-[0-9a-f]{40}\.svg$'
			match = re.match(regex, filename)
			if not match:
				continue
			note_id = match.group(1)
			if note_id in note_ids:
				filenames.append(filename)

	return filenames
