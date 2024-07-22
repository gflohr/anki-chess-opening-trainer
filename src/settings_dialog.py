# Copyright (C) 2023-2024 Guido Flohr <guido.flohr@cantanea.com>,
# all rights reserved.

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What the Fuck You Want
# to Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.

import os

from aqt import mw, AnkiQt

# pylint: disable=no-name-in-module
from aqt.qt import (QDialog, QGridLayout, # type: ignore[attr-defined]
                    QDialogButtonBox, QWidget, # type: ignore[attr-defined]
                    QTabWidget, QVBoxLayout, # type: ignore[attr-defined]
                    QCheckBox, QLabel, # type: ignore[attr-defined]
                    QRadioButton, QComboBox, # type: ignore[attr-defined]
                    QWebEngineView, QUrl, # type: ignore[attr-defined]
)


class SettingsDialog(QDialog):


	# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-statements
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		super().__init__()

		self.mw = mw

		self.setWindowTitle(_('Settings'))
		# FIXME! Do we need this?
		self.setGeometry(300, 200, 800, 600)
		self._initUI()

	def _initUI(self):
		layout = QVBoxLayout()
		self.tab_widget = QTabWidget()

		# General tab
		self.general_tab = QWidget()
		self.general_layout = QVBoxLayout()
		self.show_clock = QCheckBox(_('Show clock'))
		self.show_solutions = QCheckBox(_('Show number of correct moves'))
		self.general_layout.addWidget(self.show_clock)
		self.general_layout.addWidget(self.show_solutions)
		self.general_tab.setLayout(self.general_layout)

		# Board tab
		self.board_tab = QWidget()
		self.board_layout = QGridLayout()

		self.board_style_label = QLabel(_('Board Style:'))
		self.board_style_2d = QRadioButton("2D")
		self.board_style_3d = QRadioButton("3D")
		self.board_style_2d.setChecked(True)
		self.board_layout.addWidget(self.board_style_label, 0, 0)
		self.board_layout.addWidget(self.board_style_2d, 0, 1)
		self.board_layout.addWidget(self.board_style_3d, 0, 2)

		self.board_image_label = QLabel(_('Board:'))
		self.board_image_combo = QComboBox()
		self.populate_combo_with_images(self.board_image_combo)
		self.board_layout.addWidget(self.board_image_label, 1, 0)
		self.board_layout.addWidget(self.board_image_combo, 1, 1, 1, 2)

		self.piece_set_label = QLabel(_('Piece Set:'))
		self.piece_set_combo = QComboBox()
		self.populate_combo_with_images(self.piece_set_combo)
		self.board_layout.addWidget(self.piece_set_label, 2, 0)
		self.board_layout.addWidget(self.piece_set_combo, 2, 1, 1, 2)

		# Web view
		self.web_view = QWebEngineView()
		self.web_view.setUrl(QUrl('https://www.google.com/'))
		self.web_view.setMinimumHeight(300)
		self.board_layout.addWidget(self.web_view, 3, 0, 1, 3)

		self.board_tab.setLayout(self.board_layout)

		# Add tabs to the widget
		self.tab_widget.addTab(self.general_tab, _('General'))
		self.tab_widget.addTab(self.board_tab, _('Board'))

		# Button Box
		btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		self.button_box = QDialogButtonBox(btn)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)

		layout.addWidget(self.tab_widget)
		layout.addWidget(self.button_box)
		self.setLayout(layout)

	def populate_combo_with_images(self, combo):
		pass
		#for filename in os.listdir(directory):
		#	if filename.endswith(('.png', '.jpg', '.jpeg')):
		#		combo.addItem(QIcon(os.path.join(directory, filename)), filename)

	def accept(self) -> None:
		assert isinstance(mw, AnkiQt)

		super().accept()
