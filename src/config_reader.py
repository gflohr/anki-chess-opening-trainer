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

from aqt import mw
from aqt.utils import showCritical

from .importer_config import ImporterConfig
from .version import __version__
from .importer_config_schema import importer_config_schema
from .updater import Updater

class ConfigReader:
	# pylint: disable=too-few-public-methods
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		updater = Updater(__version__)
		raw_config = mw.addonManager.getConfig(__name__)
		raw_config = updater.update_config(raw_config)
