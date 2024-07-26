# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

from copy import deepcopy
from typing import Any, cast

from aqt import mw

from .config import Config
from .version import __version__
from .importer_config_schema import importer_config_schema
from .updater import Updater

def singleton(cls):
	instances = {}
	def get_instance(*args, **kwargs):
		if cls not in instances:
			instances[cls] = cls(*args, **kwargs)
		return instances[cls]
	return get_instance

@singleton
class ConfigReader:


	_instance = None

	def __init__(self):
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		if not hasattr(self, '_initialized'):
			updater = Updater(__version__)
			raw_config = mw.addonManager.getConfig(__name__)
			raw_config = updater.update_config(raw_config)
			self._initialized = True

	@property
	def config(self) -> Config:
		return mw.addonManager.getConfig(__name__)

	@config.setter
	def config(self, new_config: Config):
		mw.addonManager.writeConfig(__name__, new_config)
