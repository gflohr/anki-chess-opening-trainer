# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import re
from typing import Any, Dict, List, Optional, cast
import semantic_version as sv

from aqt import mw
from anki.decks import Deck, DeckId

from .importer_config import ImporterConfig
from .pgn_importer import PGNImporter
from .utils import fill_importer_config_defaults, write_importer_config
from .get_chess_model import get_chess_model


class Updater:


	# pylint: disable=too-few-public-methods
	def __init__(self, version: sv.Version):
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))
		self.mw = mw
		self.version = version
		self.addon_dir = os.path.dirname(__file__)

	def update_config(self, old: Any) -> Any:
		config = self._update(old)
		config = self._fill_config(config)

		return config

	def _update(self, raw: Any) -> Any:
		if not raw:
			raw = {}

		if 'version' not in raw or not raw['version']:
			raw['version'] = '0.0.0'

		if raw['version'] == self.version:
			return raw

		if sv.Version(raw['version']) < sv.Version('1.0.0'):
			raw = self._update_v1_0_0(raw)

		if (sv.Version(raw['version']) < sv.Version('999.0.0')):
			raw = self._update_v2_0_0(raw)

		raw['version'] = self.version

		return raw


	def _update_v1_0_0(self, raw: Any) -> Dict[str, Any]:
		raw['imports'] = {}

		if 'decks' in raw:
			decks = raw['decks']
			if 'white' in decks:
				deck_id = self.mw.col.decks.id_for_name(decks['white'])
				if deck_id:
					raw['imports'][str(deck_id)] = {
						'colour': 'white',
						'files': raw['files']['white']
					}
					raw['decks']['white'] = deck_id
			if 'black' in decks:
				deck_id = self.mw.col.decks.id_for_name(decks['black'])
				if deck_id:
					raw['imports'][str(deck_id)] = {
						'colour': 'black',
						'files': raw['files']['black']
					}
					raw['decks']['black'] = deck_id

		if 'files' in raw:
			del raw['files']

		self._patch_notes_v1_0_0(raw)

		return raw

	def _update_v2_0_0(self, raw: Any) -> Dict[str, Any]:
		if 'notetype' in raw:
			del raw['notetype']

		# The old configuration is now the importer configuration in
		# user_files.
		write_importer_config(fill_importer_config_defaults(raw))

		importer_config = cast(ImporterConfig, raw)

		self._patch_notes_v2_0_0(importer_config)

		return {}

	def _patch_notes_v1_0_0(self, config:Any):
		# pylint: disable=too-many-locals
		col = self.mw.col
		mm  = col.media
		media_dir = mm.dir()

		for _, deck_id in config['decks'].items():
			if deck_id is not None:
				for cid in col.decks.cids(deck_id):
					card = col.get_card(cid)
					note = card.note()

					pattern = r'<img src="(chess-opening-trainer-[wb]-([0-9a-f]{40})\.svg)">'
					text = note.fields[0] + note.fields[1]
					for match in re.finditer(pattern, text):
						old_name = match.group(1)
						digest = match.group(2)
						new_name = f'chess-opening-trainer-{note.id}-{digest}.svg'

						old_path = os.path.join(media_dir, old_name)
						if not Path(old_path).exists():
							continue

						with open(old_path, 'r', encoding='cp1252') as old_file:
							data = old_file.read()
							new_path = os.path.join(media_dir, new_name)
							with open(new_path, 'w', encoding='cp1252') as new_file:
								new_file.write(data)

						Path.unlink(Path(old_path), missing_ok=True)

						# We avoid col.find_and_replace() here because it goes
						# over all fields which is too unspecific for our needs.
						search = f'<img src="{old_name}">'
						replace = f'<img src="{new_name}">'
						note.fields[0] = note.fields[0].replace(search, replace)
						note.fields[1] = note.fields[1].replace(search, replace)

					col.update_note(note, skip_undo_entry=True)

	def _patch_notes_v2_0_0(self, importer_config: ImporterConfig):
		for deck_id in importer_config['imports']:
			self._migrate_deck_v2_0_0(deck_id, importer_config)

	def _migrate_deck_v2_0_0(self, deck_id: DeckId, importer_config: ImporterConfig):
		deck_data: Optional[Deck] = self.mw.col.decks.get(did=deck_id)
		if deck_data is None:
			return # No deck, no migration.
		deck = cast(Deck, deck_data)

		colour = importer_config['imports'][deck_id]['colour']
		model = get_chess_model(self.mw.col)

		importer = PGNImporter(colour=colour, model=model, deck=deck)
		files = importer_config['imports'][deck_id]['files']

		self._import_files(importer, files)


	def _import_files(self, importer: PGNImporter, files: List[str]):
		for filename in files:
			try:
				with open(filename, 'r') as file:
					importer.collect(file)
			except:
				# File was deleted, corrupt, whatever.
				pass

	def _prune_old_media_files(self):
		filenames: List[str] = []

		mm = self.mw.col.media
		media_path = mm.dir()

		for path in os.scandir(media_path):
			if not os.path.isdir(path.path):
				filename = os.path.basename(path)
				regex = r'^chess-opening-trainer-.*\.svg$'
				match = re.match(regex, filename)
				if not match:
					continue
				filenames.append(filename)

		if (len(filenames)):
			mm.trash_files(filenames)

	def _fill_config(self, raw: Any) -> Any:
		if raw is None:
			raw = {}

		if 'version' not in raw:
			raw['version'] = self.version

		return raw
