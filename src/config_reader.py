# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import sys
import semantic_version as sv

from typing import cast
from aqt import mw
from jsonschema import ValidationError, validate

from .config import Config
from .version import __version__
from .schema import schema


class ConfigReader:
	def __init__(self) -> None:
		if mw is not None:
			rawConfig = mw.addonManager.getConfig(__name__)
		else:
			rawConfig = { 'version': __version__ }

		# rawConfig = {
		# 	"colour": "white",
		# 	"decks": {
		# 			"white": "Chess::Opening::White",
		# 			"black": "Chess::Opening::Black"
		# 		},
		# 		"files": {
		# 			"white": ["/Users/guidoflohr/python/anki-chess-opening-trainer/weiss.pgn"],
		# 			"black": ["/Users/guidoflohr/python/anki-chess-opening-trainer/schwarz.pgn"]
		# 		},
		# 		"notetype": "Basic"
		# }

		self.config:Config = cast(Config, self._update(rawConfig))
		print(self.config)

		try:
			validate(self.config, schema=schema)
		except ValidationError as e:
			print(f'validation error: {e}', file=sys.stderr)
			self.config:Config = { 'version': __version__ }


	def save(self):
		if mw:
			mw.addonManager.writeConfig(__name__, self.config)


	def get_config(self):
		# Fill default values.
		if 'colour' not in self.config:
			self.config['colour'] = 'white'

		return self.config


	def _update(self, raw: any) -> Config:
		if mw is None:
			raise RuntimeError(_('Cannot upgrade without a main window!'))

		if not raw:
			raw = {}

		if 'version' not in raw or not raw['version']:
			raw['version'] = '0.0.0'

		if raw['version'] == __version__:
			return raw

		if sv.Version(raw['version']) < sv.Version('2.0.0'):
			self._update_v1_0_0(raw)

		raw['version'] = __version__

		#mw.addonManager.writeConfig(__name__, raw)

		return raw


	def _update_v1_0_0(self, raw: any):
		raw['imports'] = {}

		if 'decks' in raw:
			decks = raw['decks']
			if 'white' in decks:
				deck_id = mw.col.decks.id_for_name(decks['white'])
				if deck_id:
					raw['imports'][f'{deck_id}'] = {
						'colour': 'white',
						'files': raw['files']['white']
					}
					raw['decks']['white'] = deck_id
			if 'black' in decks:
				deck_id = mw.col.decks.id_for_name(decks['black'])
				if deck_id:
					raw['imports'][f'{deck_id}'] = {
						'colour': 'black',
						'files': raw['files']['black']
					}
					raw['decks']['black'] = deck_id

		del(raw['files'])

		raw['version'] = '1.0.0'
