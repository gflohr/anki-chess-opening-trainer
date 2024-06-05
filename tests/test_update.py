import unittest
import copy

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
		version = '1.2.3'
		updater = Updater(version)
		wanted = copy.deepcopy(default_config)
		wanted['version'] = version
		got = updater.update_config(None)
		self.assertDictEqual(wanted, got)
