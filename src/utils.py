import os
import re
import json
from typing import Any, Dict, List, Union

import anki
from anki.notes import NotetypeId
from aqt import mw

from .basic_names import basic_names

from .importer_config import ImporterConfig
from .version import __version__

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


def get_addon_dir() -> str:
	return os.path.join(os.path.dirname(__file__))


def get_importer_config_file() -> str:
	return os.path.join(get_addon_dir(), 'user_files', 'imports.json')


def write_importer_config(importer_config: ImporterConfig):
	filename = get_importer_config_file()
	with open(filename, 'w') as file:
		file.write(json.dumps(importer_config))


def get_basic_notetype() -> Union[NotetypeId, None]:
	names = []

	lang = anki.lang.current_lang
	if lang in basic_names:
		names.append(basic_names[lang])

	names.extend(list(basic_names.values()))

	for name in names:
		id_for_name = mw.col.models.id_for_name(name)
		if id_for_name is not None:
			return id_for_name

	return None


def fill_importer_config_defaults(raw: Any) -> Any:
	if raw is None:
		raw = {}

	if 'version' not in raw:
		raw['version'] = __version__

	if 'colour' not in raw:
		raw['colour'] = 'white'

	if 'decks' not in raw:
		raw['decks'] = {}

	if 'white' not in raw['decks']:
		raw['decks']['white'] = None

	if 'black' not in raw['decks']:
		raw['decks']['black'] = None

	if 'imports' not in raw:
		raw['imports'] = {}

	# FIXME! This has to be removed!
	if 'notetype' not in raw or raw['notetype'] is None or isinstance(raw['notetype'], str):
		raw['notetype'] = get_basic_notetype()

	return raw
