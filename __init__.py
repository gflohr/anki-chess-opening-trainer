import gettext
import os
import anki
from aqt import mw
from aqt.utils import qconnect
from aqt.qt import QAction
from .importDialog import ImportDialog

def showImportDialog() -> None:
	dlg = ImportDialog()
	dlg.exec()

def initI18N() -> None:
	supported = ['en', 'de']
	lang = anki.lang.current_lang
	if not lang in supported:
		lang = supported[0]

	localedir = os.path.join(os.path.dirname(__file__), 'locale')
	t = gettext.translation(
		'opening-trainer',
		localedir=localedir,
		languages=[lang])
	t.install()


def addMenuItem():
	action = QAction(_('Opening Trainer'), mw)
	# set it to call testFunction when it's clicked
	qconnect(action.triggered, showImportDialog)
	# and add it to the tools menu
	mw.form.menuTools.addAction(action)


initI18N()
addMenuItem()
