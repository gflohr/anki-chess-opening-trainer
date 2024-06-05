# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from typing import Tuple
import semantic_version as sv
import anki

from basic_names import basic_names

class Updater:
	def __init__(self, mw: any, version: sv.Version):
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

		return raw


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

		if 'notetype' not in raw or raw['notetype'] is None:
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

