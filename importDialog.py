import os
import time
from aqt import mw
from aqt.utils import showCritical, showInfo
from aqt.operations import QueryOp
from aqt.qt import (
	Qt,
	QDialog,
	QDialogButtonBox,
	QLabel,
	QGridLayout,
	QListWidget,
	QPushButton,
	QComboBox,
	QFileDialog,
)
from pathlib import Path
import sys

class _Config():
	def __init__(self):
		config = mw.addonManager.getConfig(__name__)
		col = mw.col

		if('colour' in config
		   and isinstance(config['colour'], str)
		   and 'black' == config['colour']):
			self.colour = 'black'
		else:
			self.colour = 'white'
		
		if 'notetype' in config and isinstance(config['notetype'], str):
			notetype = config['notetype']
		else:
			notetype = 'Basic'
		if notetype in list(map(lambda m: m['name'], col.models.all())):
			self.notetype = notetype
		else:
			self.notetype = None
		
		self.files = {'white': [], 'black': []}
		if 'files' in config and isinstance(config['files'], dict):
			files = config['files']
			if 'white' in files and isinstance(config['files']['white'], list):
				self.files['white'] = []
				for filename in files['white']:
					if isinstance(filename, str):
						self.files['white'].append(filename)
			if 'black' in files and isinstance(config['files']['black'], list):
				self.files['black'] = []
				for filename in files['black']:
					if isinstance(filename, str):
						self.files['black'].append(filename)

		self.decks = {'white': None, 'black': None}
		if 'decks' in config and isinstance(config['decks'], dict):
			decks = config['decks']
			if('white' in decks
			   and isinstance(decks['white'], str)
			   and decks['white'] in list(map(lambda d: d['name'], col.decks.all()))):
				self.decks['white'] = decks['white']
			if('black' in decks
			   and isinstance(decks['black'], str)
			   and decks['black'] in list(map(lambda d: d['name'], col.decks.all()))):
				self.decks['black'] = decks['black']

	def save(self, dlg: QDialog) -> None:
		colourIndex = dlg.colourCombo.currentText()
		if colourIndex == 1:
			colour = 'black'
		else:
			colour = 'white'
		self.colour = colour
		self.notetype = dlg.modelCombo.currentText()
		self.files[colour] = []
		for i in range(dlg.fileList.count()):
			self.files[colour].append(dlg.fileList.item(i).text())
		self.decks[colour] = dlg.deckCombo.currentText()
		config = {
			'colour': self.colour,
			'notetype': self.notetype,
			'files': self.files,
			'decks': self.decks,
		}

		mw.addonManager.writeConfig(__name__, config)

class ImportDialog(QDialog):
	def __init__(self) -> None:
		super().__init__()

		self.config = _Config()

		self.setWindowTitle(_('Import Opening PGN'))

		self.layout = QGridLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(QLabel(_('Input Files')), 0, 0)
		self.fileList = QListWidget()
		self.layout.addWidget(self.fileList, 0, 1)
		self.selectFileButton = QPushButton(_('Select file'))
		self.selectFileButton.clicked.connect(self._selectInputFile)
		self.layout.addWidget(self.selectFileButton, 0, 2)

		self.layout.addWidget(QLabel(_('Deck')), 1, 0)
		self.deckCombo = QComboBox()
		self.layout.addWidget(self.deckCombo, 1, 1)
		decknames: [str] = []
		for deck in mw.col.decks.all():
			decknames.append(deck['name'])
		for deckname in sorted(decknames):
			self.deckCombo.addItem(deckname)

		self.layout.addWidget(QLabel(_('Color')), 2, 0)
		self.colourCombo = QComboBox()
		self.layout.addWidget(self.colourCombo, 2, 1)
		self.colourCombo.addItem(_('White'))
		self.colourCombo.addItem(_('Black'))
		self.colourCombo.currentIndexChanged.connect(self._colourChanged)

		self.layout.addWidget(QLabel(_('Note type')), 3, 0)
		self.modelCombo = QComboBox()
		self.layout.addWidget(self.modelCombo, 3, 1)
		modelnames: [str] = []
		for model in mw.col.models.all():
			modelnames.append(model['name'])
		index = -1
		current_index = -1
		for modelname in sorted(modelnames):
			self.modelCombo.addItem(modelname)
			index += 1
			if modelname == 'Basic':
				current_index = index
		if current_index >= 0:
			self.modelCombo.setCurrentIndex(current_index)

		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.layout.addWidget(self.buttonBox, 4, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		self._fillDialog()

	def _colourChanged(self) -> None:
		if self.colourCombo.currentIndex() == 1:
			colour = 'black'
		else:
			colour = 'white'
		config = self.config

		wanted = config.decks[colour]
		for i in range(self.deckCombo.count()):
			if wanted == self.deckCombo.itemText(i):
				self.deckCombo.setCurrentIndex(i)
				break

		self.fileList.clear()
		for filename in config.files[colour]:
			self.fileList.addItem(filename)

	def _fillDialog(self) -> None:
		config = self.config
		colour = config.colour
		if 'black' == colour:
			self.colourCombo.setCurrentIndex(1)
		else:
			self.colourCombo.setCurrentIndex(0)

		if config.decks[colour] != None:
			wanted = config.decks[colour]
			for i in range(self.deckCombo.count()):
				if wanted == self.deckCombo.itemText(i):
					self.deckCombo.setCurrentIndex(i)
					break

		if config.notetype != None:
			wanted = config.notetype
			for i in range(self.modelCombo.count()):
				if wanted == self.modelCombo.itemText(i):
					self.modelCombo.setCurrentIndex(i)
					break

		self.fileList.clear()
		for filename in config.files[colour]:
			self.fileList.addItem(filename)

	def accept(self) -> None:
		def _onSuccess(count: int) -> None:
			showInfo(_('Import/Sync successfully finished'))

		def _doImport(arg) -> int:
			print(arg)
			time.sleep(3.0)
			return 42

		try:
			if not self.fileList.count():
				raise Exception(_('No input files specified!'))
			self.config.save(self)
			op = QueryOp(
				parent=mw,
				op=_doImport,
				success=_onSuccess,
			)
			op.with_progress().run_in_background()
			super().accept()
		except Exception as e:
			showCritical(str(e))
		
	def _selectInputFile(self) -> None:
		if self.fileList.count():
			dir = os.path.dirname(self.fileList.item(self.fileList.count() - 1))
		else:
			dir = None
		selection = QFileDialog.getOpenFileNames(
			self, _('Open PGN files'), dir, _('Portable Game Notation files (*.pgn)'))
		filenames = selection[0]

		if len(filenames):
			self.fileList.clear()
			self.fileList.addItems([str(Path(filename)) for filename in filenames])
