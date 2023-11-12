from aqt import mw
from aqt.utils import showInfo, showCritical
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

class _Config():
	def __init__(self):
		config = mw.addonManager.getConfig(__name__)
		col = mw.col

		if('colour' in config
		   and "<class 'str'>" == type(config['colour'])
		   and 'black' == config['colour']):
			self.colour = 'black'
		else:
			self.colour = 'white'
		
		if 'notetype' in config and "<class 'str'" == type(config['notetype']):
			notetype = config['notetype']
		else:
			notetype = 'Basic'
		if notetype in col.models.all():
			self.notetype = notetype
		else:
			self.notetype = None
		
		self.files = {'white': [], 'black': []}
		if('files' in config and "<class 'dict'>" == type(config['notetype'])):
			files = config['files']
			if 'white' in files and "<class 'list'>" == type(config['files']):
				for filename in files['white']:
					if "<class 'str'>" == type(filename):
						self.files['white'].append(filename)
			if 'black' in files and "<class 'list'>" == type(config['files']):
				for filename in files['white']:
					if "<class 'str'>" == type(filename):
						self.files['black'].append(filename)

		self.decks = {'white': None, 'black': None}
		if('decks' in config and "<class 'dict'>" == type(config['decks'])):
			decks = config['decks']
			if('white' in decks
			   and "<class 'str'>" == type(decks['white'])
			   and decks['white'] in col.decks.all()):
				self.decks['white'] = decks['white']
			if('black' in decks
			   and "<class 'str'>" == type(decks['black'])
			   and decks['black'] in col.decks.all()):
				self.decks['black'] = decks['black']


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

	def _fillDialog(self) -> None:
		config = self.config
		colour = config.colour
		if 'white' == colour:
			self.colourCombo.setCurrentIndex(0)
		else:
			self.colourCombo.setCurrentIndex(1)

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

		for filename in config.files[colour]:
			self.fileList.addItem(filename)

	def _acceptHandler(self) -> None:
		filenames: [str] = []
		lw = self.fileList
		for i in range(lw.count() - 1):
			filenames.append(lw.item(i))

		if not len(filenames):
			raise Exception(_('No input files specified!'))

	def accept(self) -> None:
		try:
			self._acceptHandler()
			super().accept()
		except Exception as e:
			showCritical(str(e))
		
	def _selectInputFile(self) -> None:
		selector = QFileDialog()
		selector.setFileMode(QFileDialog.FileMode.ExistingFiles)
		selector.setNameFilter(_('Portable Game Notation files (*.pgn)'))

		if not selector.exec():
			return
		
		filenames: [str] = selector.selectedFiles()
		if filenames:
			self.fileList.clear()
			self.fileList.addItems([str(Path(filename)) for filename in filenames])
