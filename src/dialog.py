# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
from pathlib import Path
from typing import Dict, List

from aqt import mw, AnkiQt
from aqt.operations import QueryOp
# pylint: disable=no-name-in-module
from aqt.qt import (QComboBox, QDialog,  # type: ignore[attr-defined]
                    QDialogButtonBox, QFileDialog,  # type: ignore[attr-defined]
                    QGridLayout, QLabel,  # type: ignore[attr-defined]
                    QListWidget, QListWidgetItem,  # type: ignore[attr-defined]
                    QPushButton, Qt) # type: ignore[attr-defined]
from aqt.utils import showCritical, showInfo

from .importer import Importer


class _Config():
	# pylint: disable=too-few-public-methods
	def __init__(self):
		# pylint: disable=too-many-branches

		if mw is not None:
			config = mw.addonManager.getConfig(__name__)
			if not config:
				config = {}
			col = mw.col

			if ('colour' in config and isinstance(config['colour'], str)
				and 'black' == config['colour']):
				self.colour = 'black'
			else:
				self.colour = 'white'

			if 'notetype' in config and isinstance(config['notetype'], str):
				notetype = config['notetype']
			else:
				notetype = _('Basic')
			if notetype in list(map(lambda m: m['name'], col.models.all())):
				self.notetype = notetype
			else:
				self.notetype = str(None)

			self.files: Dict[str, List[str]] = {'white': [], 'black': []}
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

			self.decks: Dict[str, str] = {}
			if 'decks' in config and isinstance(config['decks'], dict):
				decks = config['decks']
				if ('white' in decks and isinstance(decks['white'], str)
					and decks['white'] in list(
						map(lambda d: d['name'], col.decks.all()))):
					self.decks['white'] = decks['white']
				else:
					self.decks['white'] = ''
				if ('black' in decks and isinstance(decks['black'], str)
					and decks['black'] in list(
						map(lambda d: d['name'], col.decks.all()))):
					self.decks['black'] = decks['black']
				else:
					self.decks['black'] = ''


class ImportDialog(QDialog):
	# pylint: disable=too-few-public-methods, too-many-instance-attributes
	def __init__(self) -> None:
		super().__init__()

		self.config = _Config()

		self.setWindowTitle(_('Import Opening PGN'))

		self.layout = QGridLayout()
		self.setLayout(self.layout)

		self.layout.addWidget(QLabel(_('Color')), 0, 0)
		self.colour_combo = QComboBox()
		self.layout.addWidget(self.colour_combo, 0, 1)
		self.colour_combo.addItem(_('White'))
		self.colour_combo.addItem(_('Black'))
		self.colour_combo.currentIndexChanged.connect(self._colour_changed)

		self.layout.addWidget(QLabel(_('Deck')), 1, 0)
		self.deck_combo = QComboBox()
		self.layout.addWidget(self.deck_combo, 1, 1)
		decknames: [str] = []
		for deck in mw.col.decks.all():
			decknames.append(deck['name'])
		for deckname in sorted(decknames):
			self.deck_combo.addItem(deckname)

		self.layout.addWidget(QLabel(_('Input Files')), 2, 0)
		self.file_list = QListWidget()
		self.layout.addWidget(self.file_list, 2, 1)
		self.select_file_button = QPushButton(_('Select files'))
		self.select_file_button.clicked.connect(self._select_input_file)
		self.layout.addWidget(self.select_file_button, 2, 2)

		self.layout.addWidget(QLabel(_('Note type')), 3, 0)
		self.model_combo = QComboBox()
		self.layout.addWidget(self.model_combo, 3, 1)
		modelnames: [str] = []
		for model in mw.col.models.all():
			modelnames.append(model['name'])
		index = -1
		current_index = -1
		for modelname in sorted(modelnames):
			self.model_combo.addItem(modelname)
			index += 1
			if modelname == _('Basic'):
				current_index = index
		if current_index >= 0:
			self.model_combo.setCurrentIndex(current_index)

		btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		self.button_box = QDialogButtonBox(btn)
		self.layout.addWidget(self.button_box,
		                      4,
		                      0,
		                      1,
		                      3,
		                      alignment=Qt.AlignmentFlag.AlignRight)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)
		self._fill_dialog()

	def _colour_changed(self) -> None:
		if self.colour_combo.currentIndex() == 1:
			colour = 'black'
		else:
			colour = 'white'
		config = self.config

		wanted = config.decks[colour]
		for i in range(self.deck_combo.count()):
			if wanted == self.deck_combo.itemText(i):
				self.deck_combo.setCurrentIndex(i)
				break

		self.file_list.clear()
		for filename in config.files[colour]:
			self.file_list.addItem(filename)

	def _fill_dialog(self) -> None:
		config = self.config
		colour = config.colour
		if 'black' == colour:
			self.colour_combo.setCurrentIndex(1)
		else:
			self.colour_combo.setCurrentIndex(0)

		if config.decks[colour] is not None:
			wanted = config.decks[colour]
			for i in range(self.deck_combo.count()):
				if wanted == self.deck_combo.itemText(i):
					self.deck_combo.setCurrentIndex(i)
					break

		if config.notetype is not None:
			wanted = config.notetype
			for i in range(self.model_combo.count()):
				if wanted == self.model_combo.itemText(i):
					self.model_combo.setCurrentIndex(i)
					break

		self.file_list.clear()
		for filename in config.files[colour]:
			self.file_list.addItem(filename)

	def accept(self) -> None:
		assert isinstance(mw, AnkiQt)

		def _on_success(counts: tuple[int, int, int, int, int]) -> None:
			msgs = (
			    ngettext('%d note inserted.', '%d notes inserted.',
			             counts[0]) % (counts[0]),
			    ngettext('%d note updated.', '%d notes updated.', counts[1]) %
			    (counts[1]),
			    ngettext('%d note deleted.', '%d notes deleted.', counts[2]) %
			    (counts[2]),
			    ngettext('%d image created.', '%d images created.',
			             counts[3]) % (counts[3]),
			    ngettext('%d image deleted.', '%d images deleted.',
			             counts[4]) % (counts[4]),
			)
			mw.reset()
			showInfo(' '.join(msgs))

		def _do_import(config, _unused) -> tuple[int, int, int, int, int]:
			importer = Importer(
			    collection=mw.col,
			    filenames=config['files'][config['colour']],
			    notetype=config['notetype'],
			    colour=('white' == config['colour']),
			    deck_name=config['decks'][config['colour']],
			)
			return importer.run()

		try:
			if not self.file_list.count():
				raise RuntimeError(_('No input files specified!'))
			config = self.config.save(self)
			assert isinstance(mw, AnkiQt)
			op = QueryOp(
			    parent=mw,
			    op=lambda _unused: _do_import(config, _unused),
			    success=_on_success,
			)
			op.with_progress().run_in_background()
			super().accept()
		except OSError as e:
			showCritical(str(e))

	def _select_input_file(self) -> None:
		if self.file_list.count():
			item = self.file_list.item(self.file_list.count() - 1)
			assert isinstance(item, QListWidgetItem)
			directory = os.path.dirname(item.text())
		else:
			directory = None
		selection = QFileDialog.getOpenFileNames(
		    self, _('Open PGN files'), directory,
		    _('Portable Game Notation files (*.pgn)'))
		filenames = selection[0]

		if len(filenames):
			self.file_list.clear()
			self.file_list.addItems(
			    [str(Path(filename)) for filename in filenames])


def _save_config(self, dlg: ImportDialog) -> dict:
	colour_index = dlg.colour_combo.currentIndex()
	if colour_index == 1:
		colour = 'black'
	else:
		colour = 'white'
	self.colour = colour
	self.notetype = dlg.model_combo.currentText()
	self.files[colour] = []
	for i in range(dlg.file_list.count()):
		self.files[colour].append(dlg.file_list.item(i).text())
	self.decks[colour] = dlg.deck_combo.currentText()
	config = {
		'colour': self.colour,
		'notetype': self.notetype,
		'files': self.files,
		'decks': self.decks,
	}

	mw.addonManager.writeConfig(__name__, config)

	return config

_Config.save = _save_config
