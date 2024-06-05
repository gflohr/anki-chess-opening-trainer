import unittest
import copy
from unittest.mock import MagicMock
from updater import Updater


default_config = {
	'version': None,
	'colour': 'white',
	'decks': {
		'white': None,
		'black': None,
	},
	'imports': {},
	'notetype': 'Basic',
}

class TestUpdate(unittest.TestCase):
	def test_update_no_config(self):
		mw_mock = MagicMock()
		version = '1.2.3'
		updater = Updater(mw_mock, version)
		wanted = copy.deepcopy(default_config)
		wanted['version'] = version

		mw_mock.col.decks.id_for_name = MagicMock(return_value=None)

		got = updater.update_config(None)
		self.assertDictEqual(wanted, got)

	def test_update_old_default_config(self):
		mw_mock = MagicMock()
		version = '1.2.3'
		updater = Updater(mw_mock, version)
		wanted = copy.deepcopy(default_config)
		wanted['version'] = version
		old_config = {
			'colour': 'white',
			'decks': {
				'white': None,
				'black': None,
			},
			'files': {
				'white': [],
				'black': [],
			},
			'notetype': 'Basic'
		}

		mw_mock.col.decks.id_for_name = MagicMock(return_value=None)

		got = updater.update_config(old_config)
		self.assertDictEqual(wanted, got)
