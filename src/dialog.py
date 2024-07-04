# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import html
from pathlib import Path
import traceback
from typing import List, Literal, Union

from aqt import mw, AnkiQt, qconnect
from aqt.operations import QueryOp
# pylint: disable=no-name-in-module
from aqt.qt import (QComboBox, QDialog, # type: ignore[attr-defined]
                    QDialogButtonBox, QFileDialog, # type: ignore[attr-defined]
                    QGridLayout, QLabel, # type: ignore[attr-defined]
                    QListWidget, QListWidgetItem, # type: ignore[attr-defined]
                    QPushButton, Qt, QMessageBox, # type: ignore[attr-defined]
					QDesktopServices, QUrl) # type: ignore[attr-defined]
from aqt.utils import showCritical, showInfo, showWarning
from anki.utils import no_bundled_libs

from .config import Config

from .importer import Importer
from .config_reader import ConfigReader


class ImportDialog(QDialog):


	# pylint: disable=too-few-public-methods, too-many-instance-attributes
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		super().__init__()

		self.mw = mw
		self.config = ConfigReader().get_config()

		self.setWindowTitle(_('Import PGN File'))

		layout = QGridLayout()
		self.setLayout(layout)

		layout.addWidget(QLabel(_('Color')), 0, 0)
		self.colour_combo = QComboBox()
		layout.addWidget(self.colour_combo, 0, 1)
		self.colour_combo.addItem(_('White'))
		self.colour_combo.addItem(_('Black'))
		self.updating = False
		self.colour_combo.currentIndexChanged.connect(self._colour_changed)

		layout.addWidget(QLabel(_('Deck')), 1, 0)
		self.deck_combo = QComboBox()
		layout.addWidget(self.deck_combo, 1, 1)
		decknames: List[str] = []
		if mw is not None:
			for deck in mw.col.decks.all():
				decknames.append(deck['name'])

		for deckname in sorted(decknames):
			self.deck_combo.addItem(deckname)
		self.deck_combo.currentIndexChanged.connect(self._deck_changed)

		layout.addWidget(QLabel(_('Input Files')), 2, 0)
		self.file_list = QListWidget()
		layout.addWidget(self.file_list, 2, 1)
		self.select_file_button = QPushButton(_('Select files'))
		self.select_file_button.clicked.connect(self._select_input_file)
		layout.addWidget(self.select_file_button, 2, 2)

		layout.addWidget(QLabel(_('Note type')), 3, 0)
		self.model_combo = QComboBox()
		layout.addWidget(self.model_combo, 3, 1)
		modelnames: List[str] = []
		if mw is not None:
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
		layout.addWidget(self.button_box,
		                 4,
		                 0,
		                 1,
		                 3,
		                 alignment=Qt.AlignmentFlag.AlignRight)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)
		self._fill_dialog()

	def _colour_changed(self) -> None:
		if self.updating:
			return
		self.updating = True

		if self.colour_combo.currentIndex() == 1:
			colour = 'black'
		else:
			colour = 'white'
		config = self.config

		deck_id = config['decks'][colour]
		deck = self.mw.col.decks.get(deck_id)
		if deck is not None:
			name = deck['name']
			for i in range(self.deck_combo.count()):
				if name == self.deck_combo.itemText(i):
					self.deck_combo.setCurrentIndex(i)
					break

			self.file_list.clear()

			if str(deck_id) in config['imports']:
				record = config['imports'][str(deck_id)]
				for filename in record['files']:
					self.file_list.addItem(filename)

		self.updating = False

	def _deck_changed(self):
		if self.updating:
			return
		self.updating = True

		self.file_list.clear()

		deck_name = self.deck_combo.currentText()
		deck_id = self.mw.col.decks.id_for_name(deck_name)
		if deck_id is not None and str(deck_id) in self.config['imports']:
			record = self.config['imports'][str(deck_id)]
			self._set_colour_combo(record['colour'])

			for filename in record['files']:
				self.file_list.addItem(filename)

		self.updating = False

	def _set_colour_combo(self, colour: Literal['white', 'black']):
		if 'black' == colour:
			self.colour_combo.setCurrentIndex(1)
		else:
			self.colour_combo.setCurrentIndex(0)

	def _fill_dialog(self) -> None:
		config = self.config
		colour = config['colour']
		if colour is None:
			colour = 'white'

		self._set_colour_combo(colour)

		self.file_list.clear()

		if config['decks'][colour] is not None:
			deck_id = config['decks'][colour]
			deck = self.mw.col.decks.get(did=deck_id, default=False)

			# The deck may have been deleted in the meantime.
			if deck:
				for i in range(self.deck_combo.count()):
					if deck['name'] == self.deck_combo.itemText(i):
						self.deck_combo.setCurrentIndex(i)

			self.file_list.clear()
			if str(deck_id) in config['imports']:
				record = config['imports'][str(deck_id)]
				for filename in record['files']:
					self.file_list.addItem(filename)
					break

		if config['notetype'] is not None:
			notetype_id = config['notetype']
			name = self.mw.col.models.get(notetype_id)
			if name is not None:
				for i in range(self.model_combo.count()):
					if name == self.model_combo.itemText(i):
						self.model_combo.setCurrentIndex(i)
						break

	def accept(self) -> None:
		assert isinstance(mw, AnkiQt)

		def _on_success(counts: Union[Exception, tuple[int, int, int, int, int]]):
			if isinstance(counts, Exception):
				self._show_exception(counts)
				return

			if sum(counts) == 0:
				msg = _('No changes since last import into this deck.')
			else:
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
				msg = ' '.join(msgs)

			mw.reset()
			mw.addonManager.writeConfig(__name__, self.config)

			showInfo(msg)

		def _do_import(_) -> Union[Exception, tuple[int, int, int, int, int]]:
			try:
				colour = self.config['colour']
				deck_id = self.config['decks'][colour]
				record = self.config['imports'][str(deck_id)]
				filenames = record['files']
				notetype_id = self.config['notetype']

				importer = Importer(
					collection=mw.col,
					deck_id=deck_id,
					notetype_id=notetype_id,
					filenames=filenames,
					colour=('white' == colour),
				)
				return importer.run()
			except Exception as e:
				return e

		if not self.file_list.count():
			raise RuntimeError(_('No input files specified!'))
		self.config = self._save_config()
		if self.config is None:
			self.reject()
		else:
			assert isinstance(mw, AnkiQt)
			op = QueryOp(
				parent=mw,
				op=lambda _unused: _do_import(_unused),
				success=_on_success,
			)
			op.with_progress().run_in_background()
			super().accept()

	def _show_exception(self, e: Exception):
		ftb = list(traceback.format_tb(e.__traceback__))

		msgs = (
			_('An error occurred!'),
			_('Clicking the help button will open a web page explaining how to report a bug.'),
			_('Please include the following information in your bug report:'),
			'<hr />',
			_('Exception type:') + ' ' + html.escape(type(e).__name__),
			_('Exception message:') + ' ' + html.escape(str(e)),
			_('Traceback:'),
		)
		msg = '<br />'.join(msgs) + '<br  />'.join(ftb)
		print(msg)

		parent = self.mw.app.activeWindow() or mw
		msg_box = QMessageBox(parent)
		msg_box.setIcon(QMessageBox.Icon.Critical)
		msg_box.setTextFormat(Qt.TextFormat.MarkdownText)
		msg_box.setText(msg)
		msg_box.setWindowTitle(_('Chess Opening Trainer'))

		# This is the reason, whey the customBtn argument for `showInfo()`
		# cannot be used.  You can only call setDefault() or use
		# qconnect() with the return value of addButton() which is a
		# pointer to QPushButton.
		ok_button = msg_box.addButton(QMessageBox.StandardButton.Ok)
		if ok_button is not None:
			ok_button.setDefault(True)

		def open_link(link: str):
			with no_bundled_libs():
				QDesktopServices.openUrl(QUrl(link))

		help_button = msg_box.addButton(QMessageBox.StandardButton.Help)
		if help_button is not None:
			link = _('https://www.guido-flohr.net/practice-chess-openings-with-anki/#report-bugs')
			help_button.clicked.connect(open_link(link))
			help_button.setAutoDefault(False)

		return msg_box.exec()

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

	def _save_config(self) -> Config | None:
		colour_index = self.colour_combo.currentIndex()
		if colour_index == 1:
			colour = 'black'
		else:
			colour = 'white'

		col = self.mw.col

		deck_name = self.deck_combo.currentText()
		deck_id = col.decks.id_for_name(deck_name)
		if deck_id is None:
			showWarning(_('The selected deck does not exist! Try again!'))
			return None

		notetype_name = self.model_combo.currentText()

		notetype_id = col.models.id_for_name(notetype_name)
		if notetype_id is None:
			showWarning(_('The selected note type does not exist! Try again!'))
			return None

		files: List[str] = []
		for i in range(self.file_list.count()):
			item = self.file_list.item(i)
			if item is not None:
				files.append(item.text())

		self.config['colour'] = colour
		self.config['decks'][colour] = deck_id

		self.config['imports'][str(deck_id)] = {
			'colour': colour,
			'files': files,
		}

		self.config['notetype'] = notetype_id

		return self.config
