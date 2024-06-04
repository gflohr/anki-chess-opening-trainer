# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import semantic_version as sv

from typing import List, cast
from aqt import mw

from .config_schema import ConfigSchema
from .version import __version__


class Config:
	def __init__(self) -> None:
		if mw is not None:
			rawConfig = mw.addonManager.getConfig(__name__)

		self.config:ConfigSchema = cast(ConfigSchema, self._update(rawConfig))
		print(self.config)


	def _update(self, raw: any) -> ConfigSchema:
		if not raw:
			raw = {}

		if 'version' not in raw or not raw['version']:
			raw['version'] = '0.0.0'

		if sv.Version(raw['version']) < sv.Version('1.0.0'):
			self._update_v1_0_0(raw)

		raw['version'] = __version__

		return raw


	def _update_v1_0_0(self, raw: any):
		if mw is None:
			raise RuntimeError(_('Cannot upgrade without a main window!'))

		raw['imports'] = {}

		if 'decks' in raw:
			decks = raw['decks']
			if 'white' in decks:
				deck_id = mw.col.decks.id_for_name(decks['white'])
				if deck_id:
					raw['imports'][deck_id] = {
						'colour': 'white',
						'files': raw['files']['white']
					}
			if 'black' in decks:
				deck_id = mw.col.decks.id_for_name(decks['black'])
				if deck_id:
					raw['imports'][deck_id] = {
						'colour': 'black',
						'files': raw['files']['black']
					}

		del(raw['files'])

		raw['version'] = '1.0.0'
