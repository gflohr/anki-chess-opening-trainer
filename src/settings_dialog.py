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
                    QDialogButtonBox, Qt) # type: ignore[attr-defined]


class SettingsDialog(QDialog):


	# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-statements
	def __init__(self) -> None:
		if mw is None:
			raise RuntimeError(_('Cannot run without main window!'))

		super().__init__()

		self.mw = mw

		self.setWindowTitle(_('Settings'))

		layout = QGridLayout()
		self.setLayout(layout)

		btn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		self.button_box = QDialogButtonBox(btn)
		layout.addWidget(self.button_box,
		                 0,
		                 0,
		                 1,
		                 1,
		                 alignment=Qt.AlignmentFlag.AlignRight)
		self.button_box.accepted.connect(self.accept)
		self.button_box.rejected.connect(self.reject)
	def accept(self) -> None:
		assert isinstance(mw, AnkiQt)

		super().accept()
