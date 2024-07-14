import os
import re
import json
from typing import Any, List, cast
from jsonschema import ValidationError, validate

import anki
from anki.notes import NotetypeId
from aqt import mw
from aqt.utils import show_critical


import importer_config_schema

from .importer_config import ImporterConfig
from .version import __version__

# FIXME! No longer needed!
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


def _get_importer_config_filename() -> str:
	return os.path.join(get_addon_dir(), 'user_files', 'imports.json')


def load_importer_config() -> ImporterConfig:
		importer_filename = _get_importer_config_filename()
		if (os.path.exists(importer_filename)):
			with open(importer_filename, 'r') as file:
				raw_importer_config = json.load(file)
		else:
			raw_importer_config = _fill_importer_config_defaults(None)

		try:
			validate(raw_importer_config, schema=importer_config_schema)
		except ValidationError as e:
			show_critical(_('Your imports configuration is invalid, restoring defaults.'))
			raw_importer_config = _fill_importer_config_defaults(None)
			write_importer_config(raw_importer_config)
			print(e)

		return cast(ImporterConfig, raw_importer_config)


def write_importer_config(importer_config: ImporterConfig):
	importer_config = _fill_importer_config_defaults(importer_config)
	filename = _get_importer_config_filename()
	with open(filename, 'w') as file:
		file.write(json.dumps(importer_config))


def _fill_importer_config_defaults(raw: Any) -> Any:
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

	return raw

piece_translations = {
	'D': 'Q',
	'T': 'R',
	'L': 'B',
	'S': 'N',
	# All these keys are cyrillic letters!
	'Д': 'Q',
	'Т': 'R',
	'О': 'B',
	'К': 'N',
}

piece_pattern = re.compile('|'.join(re.escape(p) for p in piece_translations.keys()))

def normalize_move(moves: str):
	def replace_match(match: re.Match):
		return piece_translations[match.group()]

	return piece_pattern.sub(replace_match, moves)
