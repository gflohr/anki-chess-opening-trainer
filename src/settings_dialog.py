# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os
import json
from typing import Dict
from aqt import mw, AnkiQt

# pylint: disable=no-name-in-module
from aqt.qt import (
	QDialog, QGridLayout, QSize, QComboBox, # type: ignore[attr-defined]
	QDialogButtonBox, QWidget, QStyleFactory, # type: ignore[attr-defined]
	QTabWidget, QVBoxLayout, # type: ignore[attr-defined]
	QCheckBox, QLabel, # type: ignore[attr-defined]
	QRadioButton, QComboBox, # type: ignore[attr-defined]
	QWebEngineView, QUrl, QUrlQuery, # type: ignore[attr-defined]
	Qt, QHBoxLayout, QIcon, # type: ignore[attr-defined]
)

from .config_reader import ConfigReader
from .image_paths import (
	piece_images_2d, piece_images_3d,
	board_images_2d, board_images_3d,
)


class ThumbnailComboBox(QComboBox):
	def sizeHint(self):
		return QSize(super().sizeHint().width(), 36)

orientations = {
	'Automatic': 0,
	'White': 1,
	'Black': 2,
}

class SettingsDialog(QDialog):


	# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-statements
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		super().__init__()

		self.mw = mw
		self._config_reader = ConfigReader()
		self._config = self._config_reader.config
		pkg = __name__.split('.')[0]
		port = mw.mediaServer.getPort()
		self._base_url = QUrl(f'http://127.0.0.1:{port}')
		self._base_url.setPath(f'/_addons/{pkg}/assets/html/index.html')

		self.setWindowTitle(_('Settings'))

		self._initUI()

	def _initUI(self):
		layout = QVBoxLayout()

		self.tab_widget = QTabWidget()
		self._initBoardTab()
		self._initStudyingTab()

		# Button Box
		btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		self.button_box = QDialogButtonBox(btn)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		layout.addWidget(self.tab_widget)
		layout.addWidget(self.button_box)
		self.setLayout(layout)

	def _initBoardTab(self):
		self.board_tab = QWidget()
		self.board_layout = QGridLayout()
		self.board_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

		row = 0;
		self.board_style_label = QLabel(_('Board Style:'))
		self.board_style_2d = QRadioButton("2D")
		self.board_style_2d.setChecked(not self._config['board']['3D'])
		self.board_style_3d = QRadioButton("3D")
		self.board_style_3d.setChecked(self._config['board']['3D'])
		self.board_style_layout = QHBoxLayout()
		self.board_style_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		self.board_style_layout.addWidget(self.board_style_2d)
		self.board_style_layout.addWidget(self.board_style_3d)

		self.board_layout.addWidget(self.board_style_label, row, 0)
		self.board_layout.addLayout(self.board_style_layout, row, 1)
		row = row + 1

		self.board_image_label = QLabel(_('Board:'))
		self.board_image_combo = ThumbnailComboBox()
		self.board_image_combo.setIconSize(QSize(64, 32))
		self.board_image_combo.setMinimumHeight(36)
		self.board_image_combo.setStyle(QStyleFactory.create('Fusion'))
		self.board_layout.addWidget(self.board_image_label, row, 0)
		self.board_layout.addWidget(self.board_image_combo, row, 1, 1, 2)
		row = row + 1

		self.piece_set_label = QLabel(_('Piece Set:'))
		self.piece_set_combo = ThumbnailComboBox()
		self.piece_set_combo.setIconSize(QSize(64, 64))
		self.piece_set_combo.setMinimumHeight(68)
		self.piece_set_combo.setStyle(QStyleFactory.create('Fusion'))
		self.board_layout.addWidget(self.piece_set_label, row, 0)
		self.board_layout.addWidget(self.piece_set_combo, row, 1, 1, 2)
		row = row + 1

		orientation_label = QLabel(_('Board orientation'))
		orientation_combo = QComboBox()
		orientation_combo.addItem(_('Automatic'))
		orientation_combo.addItem(_('White'))
		orientation_combo.addItem(_('Black'))
		currentIndex = orientations[self._config['board']['orientation']]
		orientation_combo.setCurrentIndex(currentIndex)
		orientation_combo.setToolTip(
			'Set the board orientation:\n'
			'- White: View from White\'s perspective.\n'
			'- Black: View from Black\'s perspective.\n'
			'- Automatic: View from the perspective of the side to move.'
		)
		self.board_layout.addWidget(orientation_label, row, 0)
		self.board_layout.addWidget(orientation_combo, row, 1, 1, 2)
		row = row + 1

		clock_label = QLabel(_('Display clock'))
		clock_checbkox = QCheckBox()
		clock_checbkox.setChecked(self._config['board']['displayClock'])
		self.board_layout.addWidget(clock_label, row, 0)
		self.board_layout.addWidget(clock_checbkox, row, 1, 1, 2)
		row = row + 1

		self._fill_thumbnail_combos()

		# Web view
		self.web_view = QWebEngineView()
		self.web_view.setUrl(self._get_url())
		self.web_view.setMinimumHeight(300)
		self.board_layout.addWidget(self.web_view, row, 0, 1, 3)

		self.board_tab.setLayout(self.board_layout)

		self.tab_widget.addTab(self.board_tab, _('Board'))

		# Connect signals.
		self.board_style_3d.toggled.connect(self._on_board_style_toggled)
		self.board_image_combo.currentIndexChanged.connect(self._on_board_changed)
		self.piece_set_combo.currentIndexChanged.connect(self._on_piece_set_changed)

	def _initStudyingTab(self):
		studying_tab = QWidget()
		studying_layout = QGridLayout()
		studying_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

		row = 0

		show_num_answers_label = QLabel(_('Show number of answers:'))
		show_num_answers_checkbox = QCheckBox()
		show_num_answers_checkbox.setChecked(self._config['studying']['showNumberOfAnswers'])
		show_num_answers_checkbox.setToolTip(_('''
If this is checked, the number of rows for the moves to enter will correspond
with the expected number of moves.
''').strip())
		studying_layout.addWidget(show_num_answers_label, row, 0)
		studying_layout.addWidget(show_num_answers_checkbox, row, 1)
		row = row + 1

		auto_turn_label = QLabel(_('Turn card automatically:'))
		auto_turn_checkbox = QCheckBox()
		auto_turn_checkbox.setChecked(self._config['studying']['autoTurnCard'])
		# If "show number of answers" is switched off, automatically turning
		# the card would void the idea of that setting.
		auto_turn_checkbox.setCheckable(self._config['studying']['showNumberOfAnswers'])
		auto_turn_checkbox.setToolTip(_('''
If this is checked, the card is automatically turned, when all expected moves
have been entered.  Unchecking this is only possible if you have also switched
displaying the number of answers.
''').strip())
		studying_layout.addWidget(auto_turn_label, row, 0)
		studying_layout.addWidget(auto_turn_checkbox, row, 1)
		row = row + 1

		studying_tab.setLayout(studying_layout)

		self.tab_widget.addTab(studying_tab, _('Studying'))

	def _get_url(self) -> QUrl:
		url = QUrl(self._base_url)
		query = QUrlQuery(url)
		query.addQueryItem('configure', '1')
		query.addQueryItem('config', json.dumps(self._config))
		url.setQuery(query)

		return url

	def _fill_thumbnail_combos(self):
		self._fill_board_combo()
		self._fill_piece_set_combo()

	def _fill_board_combo(self):
		if self._config['board']['3D']:
			boards = board_images_3d
			selected = self._config['board']['3Dboard']
		else:
			boards = board_images_2d
			selected = self._config['board']['2Dboard']
		index = 0
		self.board_image_combo.clear()
		for board_spec in boards:
			self.board_image_combo.addItem(QIcon(board_spec[0]), board_spec[1])
			if selected == board_spec[1]:
				self.board_image_combo.setCurrentIndex(index)
			index = index + 1

	def _fill_piece_set_combo(self):
		if self._config['board']['3D']:
			pieces = piece_images_3d
			selected = self._config['board']['3Dpieces']
		else:
			pieces = piece_images_2d
			selected = self._config['board']['2Dpieces']
		index = 0
		self.piece_set_combo.clear()
		for piece_spec in pieces:
			self.piece_set_combo.addItem(QIcon(piece_spec[0]), piece_spec[1])
			if selected == piece_spec[1]:
				self.piece_set_combo.setCurrentIndex(index)
			index = index + 1

	def accept(self) -> None:
		self._config_reader.config = self._config
		super().accept()

	def _on_board_style_toggled(self):
		self._config['board']['3D'] = not self._config['board']['3D']
		self.board_style_2d.setChecked(not self._config['board']['3D'])
		self.board_style_3d.setChecked(self._config['board']['3D'])
		self._fill_thumbnail_combos()
		self._update_webview()

	def _on_board_changed(self):
		selected = self.board_image_combo.currentText()
		if self._config['board']['3D']:
			self._config['board']['3Dboard'] = selected
		else:
			self._config['board']['2Dboard'] = selected
		self._update_webview()

	def _on_piece_set_changed(self):
		selected = self.piece_set_combo.currentText()
		if self._config['board']['3D']:
			self._config['board']['3Dpieces'] = selected
		else:
			self._config['board']['2Dpieces'] = selected
		self._update_webview()

	def _update_webview(self):
		escaped = json.dumps(json.dumps(self._config))
		code = f"window.chessOpeningTrainerUpdateConfig({escaped})"
		self.web_view.page().runJavaScript(code)
