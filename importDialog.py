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

class ImportDialog(QDialog):
	def __init__(self) -> None:
		super().__init__()

		self.setWindowTitle(_('Import Opening PGN'))

		self.layout = QGridLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(QLabel(_('Input Files')), 0, 0)
		self.fileList = QListWidget()
		self.layout.addWidget(self.fileList, 0, 1)
		self.selectFileButton = QPushButton(_('Select file'))
		self.selectFileButton.clicked.connect(self.selectInputFile)
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

	def acceptHandler(self) -> None:
		filenames: [str] = []
		lw = self.fileList
		for i in range(lw.count() - 1):
			filenames.append(lw.item(i))

		if not len(filenames):
			raise Exception(_('No input files specified!'))

	def accept(self) -> None:
		try:
			self.acceptHandler()
			super().accept()
		except Exception as e:
			showCritical(str(e))
		
	def selectInputFile(self) -> None:
		selector = QFileDialog()
		selector.setFileMode(QFileDialog.FileMode.ExistingFiles)
		selector.setNameFilter(_('Portable Game Notation files (*.pgn)'))

		if not selector.exec():
			return
		
		filenames: [str] = selector.selectedFiles()
		if filenames:
			self.fileList.clear()
			self.fileList.addItems([str(Path(filename)) for filename in filenames])
