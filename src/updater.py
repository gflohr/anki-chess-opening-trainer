# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import re
from pathlib import Path
from typing import List
import semantic_version as sv
import anki
from anki.media import MediaManager

from basic_names import basic_names
from config import Config

class Updater:
	def __init__(self, mw: MediaManager, version: sv.Version):
		self.mw = mw
		self.version = version


	def update_config(self, old: any) -> any:
		config = self._update(old)
		config = self._fill_config(config)

		return config

	def _update(self, raw: any) -> any:
		if not raw:
			raw = {}

		if 'version' not in raw or not raw['version']:
			raw['version'] = '0.0.0'

		if raw['version'] == self.version:
			return raw

		if sv.Version(raw['version']) < sv.Version('1.0.0'):
			raw = self._update_v1_0_0(raw)

		raw['version'] = self.version

		return raw


	def _update_v1_0_0(self, raw: any):
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
			del(raw['files'])

		raw['version'] = '1.0.0'

		self._patch_notes_v1_0_0(raw)

		return raw

	def _patch_notes_v1_0_0(self, config:Config):
		col = self.mw.col
		mm  = col.media
		media_dir = mm.dir()

		for colour, deck_id in config['decks'].items():
			if deck_id is not None:
				c = colour[0]
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

	def _fill_config(self, raw: any) -> any:
		if raw is None:
			raw = {}

		if 'version' not in raw:
			raw['version'] = self.version

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

		if 'notetype' not in raw or raw['notetype'] is None or isinstance(raw['notetype'], str):
			raw['notetype'] = self._get_basic_notetype()

		return raw

	def _get_basic_notetype(self):
		names = []

		lang = anki.lang.current_lang
		if lang in basic_names:
			names.append(basic_names[lang])

		names.extend(list(basic_names.values()))

		for name in names:
			id = self.mw.col.models.id_for_name(name)
			if id is not None:
				return id

		return None

