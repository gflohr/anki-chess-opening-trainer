# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import gettext
import os
import sys
import importlib

import anki
from aqt import mw, gui_hooks
# pylint: disable=no-name-in-module
from aqt.qt import QAction, QMenu # type: ignore[attr-defined]
from aqt.utils import qconnect


moduledir = os.path.dirname(__file__)
sys.path.append(moduledir)
sys.path.append(os.path.join(moduledir, 'vendor'))

# pylint: disable=wrong-import-order, wrong-import-position
from .import_dialog import ImportDialog
from .settings_dialog import SettingsDialog
from .config import Config
from .importer_config import ImporterConfig

# These will be initialized, when the main window appears.
importer_config: ImporterConfig = None
config: Config = None

def show_import_dialog() -> None:
	dlg = ImportDialog()
	dlg.exec()

def show_settings_dialog() -> None:
	dlg = SettingsDialog()
	dlg.exec()

def init_i18n() -> None:
	supported = ['en', 'en-GB', 'de']
	lang = anki.lang.current_lang
	if lang not in supported:
		lang = supported[0]

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation('anki-chess-opening-trainer',
	                        localedir=localedir,
	                        languages=[lang])
	t.install(names=['_', 'ngettext'])

def init_web() -> None:
	mw.addonManager.setWebExports(__name__, r'.*(css|js|jpg|svg|png|json)')

def add_menu_item():
	if mw is not None:
		menu = QMenu(_('Chess Opening Trainer'), mw.form.menuTools)

		import_action = QAction(_('Import PGN Files...'), mw)
		qconnect(import_action.triggered, show_import_dialog)
		menu.addAction(import_action)

		settings_action = QAction(_('Settings...'), mw)
		qconnect(settings_action.triggered, show_settings_dialog)
		menu.addAction(settings_action)

		mw.form.menuTools.addMenu(menu)

def load_config():
	pkg = mw.addonManager.addonFromModule(__name__)
	config_reader_module = importlib.import_module(f'{pkg}.config_reader')
	ConfigReader = getattr(config_reader_module, 'ConfigReader')
	ConfigReader()


init_i18n()
init_web()
add_menu_item()
gui_hooks.main_window_did_init.append(load_config)
