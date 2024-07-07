# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import json
from typing import Any, cast
from jsonschema import ValidationError, validate

from aqt import mw
from aqt.utils import showCritical

from .importer_config import ImporterConfig
from .version import __version__
from .importer_config_schema import importer_config_schema
from .updater import Updater
from .utils import fill_importer_config_defaults, get_importer_config_file, write_importer_config

class ConfigReader:
	# pylint: disable=too-few-public-methods
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		updater = Updater(__version__)
		raw_config = mw.addonManager.getConfig(__name__)
		raw_config = updater.update_config(raw_config)

		importer_filename = get_importer_config_file()
		if (os.path.exists(importer_filename)):
			with open(importer_filename, 'r') as file:
				raw_importer_config = json.load(file)
		else:
			raw_importer_config = fill_importer_config_defaults(None)

		try:
			validate(raw_importer_config, schema=importer_config_schema)
		except ValidationError as e:
			showCritical(_('Your imports configuration is invalid, restoring defaults.'))
			raw_importer_config = fill_importer_config_defaults(None)
			write_importer_config(raw_importer_config)
			print(e)

		self.importer_config:ImporterConfig = cast(ImporterConfig, raw_importer_config)


	def get_importer_config(self):
		return self.importer_config


	def get_config(self):
		return self.config
