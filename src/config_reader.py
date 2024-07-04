# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from typing import Any, cast
from jsonschema import ValidationError, validate

from aqt import mw
from aqt.utils import showCritical

from .config import Config
from .version import __version__
from .schema import schema
from .updater import Updater


class ConfigReader:
	# pylint: disable=too-few-public-methods
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		raw_config = mw.addonManager.getConfig(__name__)

		updater = Updater(__version__)
		raw_config = updater.update_config(raw_config)

		try:
			validate(raw_config, schema=schema)
			mw.addonManager.writeConfig(__name__, cast(dict[Any, Any], raw_config))
		except ValidationError:
			showCritical(_('Your add-on configuration is invalid, restoring defaults.'))
			raw_config = updater.update_config(None)

		self.config:Config = cast(Config, raw_config)


	def get_config(self):
		return self.config
