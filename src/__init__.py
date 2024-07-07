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

import anki
from aqt import mw
# pylint: disable=no-name-in-module
from aqt.qt import QAction # type: ignore[attr-defined]
from aqt.utils import qconnect

moduledir = os.path.dirname(__file__)
sys.path.append(moduledir)
sys.path.append(os.path.join(moduledir, 'vendor'))

# pylint: disable=wrong-import-order, wrong-import-position
from .dialog import ImportDialog
from .delete_hook import DeleteHook

def show_import_dialog() -> None:
	dlg = ImportDialog()
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
	mw.addonManager.setWebExports(__name__, r'assets/.*(css|js|jpg|svg|png)')


def add_menu_item():
	action = QAction(_('Chess Opening Trainer'), mw)
	# set it to call testFunction when it's clicked
	qconnect(action.triggered, show_import_dialog)
	# and add it to the tools menu
	if mw is not None:
		mw.form.menuTools.addAction(action)



init_i18n()
init_web()
DeleteHook().installHook()
add_menu_item()
