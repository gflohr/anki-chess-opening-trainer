import gettext
import os
import sys
import anki
from aqt import mw
from aqt.utils import qconnect
from aqt.qt import QAction

moduledir = os.path.dirname(__file__)
sys.path.append(moduledir)
sys.path.append(os.path.join(moduledir, 'lib'))

from importDialog import ImportDialog

def showImportDialog() -> None:
	dlg = ImportDialog()
	dlg.exec()

def initI18N() -> None:
	supported = ['en', 'en-GB', 'de']
	lang = anki.lang.current_lang
	print(lang, file=sys.stderr)
	if not lang in supported:
		lang = supported[0]

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation(
		'opening-trainer',
		localedir=localedir,
		languages=[lang])
	t.install(names=['ngettext'])

def addMenuItem():
	action = QAction(_('Opening Trainer'), mw)
	# set it to call testFunction when it's clicked
	qconnect(action.triggered, showImportDialog)
	# and add it to the tools menu
	mw.form.menuTools.addAction(action)


initI18N()
addMenuItem()
