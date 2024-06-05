# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import sys

from typing import cast
from aqt import mw
from jsonschema import ValidationError, validate

from .config import Config
from .version import __version__
from .schema import schema
from .updater import Updater


class ConfigReader:
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window'))

		raw_config = mw.addonManager.getConfig(__name__)

		updater = Updater(mw, __version__)
		config = updater.update_config(raw_config)
		self.config:Config = cast(Config, config)

		try:
			validate(self.config, schema=schema)
			mw.addonManager.writeConfig(__name__, self.config)
		except ValidationError as e:
			print(f'error validating Chess Opening Trainer configuration:')
			print(e)
			config = updater.update_config(None)
			self.config:Config = cast(Config, config)


	def get_config(self):
		return self.config
