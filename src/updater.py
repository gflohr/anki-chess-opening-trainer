# Copyright (C) 2023-2026 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import re
from pathlib import Path
from typing import Any, Union
import semantic_version as sv
import anki
from aqt import mw
from anki.notes import NotetypeId
from anki.decks import DeckId

from .basic_names import basic_names

class Updater:


	# pylint: disable=too-few-public-methods
	def __init__(self, version: sv.Version, anki_mw=mw):
		if anki_mw is None:
			raise RuntimeError(_('Cannot run without main window!'))
		self.mw = anki_mw
		self.version = version


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

		if sv.Version(raw['version']) < sv.Version('1.2.0'):
			raw = self._update_v1_2_0(raw)

		raw['version'] = self.version

		return raw

	def _update_v1_2_0(self, raw: Any):
		if 'imports' not in raw:
			return raw

		col = self.mw.col
		pattern = re.compile(r'<a href="(https://lichess\.org/analysis[^"]*)"')

		def replace_href(match: re.Match) -> str:
			url = match.group(1)
			return f'<a href="{url.replace(' ', '_').replace('%20', '_')}"'

		for id in raw['imports']:
			deck_id = DeckId(id)
			deck = col.decks.get(deck_id)
			if not deck:
				continue

			for cid in col.decks.cids(deck_id):
				card = col.get_card(cid)
				note = card.note()

				if len(note.fields) <= 1:
					continue

				answer_text = note.fields[1]

				# This will not fully migrate the Lichess links to the new
				# version with a full analysis of the entire PGN. This is not
				# easily possible, because it requires the entire game history,
				# which is not present at this point.
				#
				# We could check if the imported files are still present, but
				# re-importing behind the user's back, is not acceptable.
				#
				# We could also parse the moves, and try to recover the game
				# history from that but that is only possible, if the original
				# game started at the standard starting position.
				#
				# Long story short: It is not worth the hassle. Most people
				# will have the PGN files on disk and can easily re-import
				# them.
				updated_text = pattern.sub(replace_href, answer_text)

				if updated_text != answer_text:
					note.fields[1] = updated_text
					col.update_note(note, skip_undo_entry=True)

		raw['version'] = '1.2.0'

		return raw

	def _update_v1_0_0(self, raw: Any):
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

		raw['version'] = '1.0.0'

		self._patch_notes_v1_0_0(raw)

		return raw

	def _patch_notes_v1_0_0(self, config:Any):
		# pylint: disable=too-many-locals
		col = self.mw.col
		mm  = col.media
		media_dir = mm.dir()

		for _, deck_id in config.get('decks', {}).items():
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

	def _fill_config(self, raw: Any) -> Any:
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

	def _get_basic_notetype(self) -> Union[NotetypeId, None]:
		names = []

		lang = anki.lang.current_lang
		if lang in basic_names:
			names.append(basic_names[lang])

		names.extend(list(basic_names.values()))

		for name in names:
			id_for_name = self.mw.col.models.id_for_name(name)
			if id_for_name is not None:
				return id_for_name

		return None
