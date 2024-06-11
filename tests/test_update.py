import unittest
import copy
from unittest.mock import MagicMock, patch
from updater import Updater


WHITE_DECK_NAME = 'Chess::Opening::White'
BLACK_DECK_NAME = 'Chess::Opening::Black'

WHITE_DECK_ID = 123456789
BLACK_DECK_ID = 987654321

WHITE_FILES = [
	'/path/to/chess/white-open.pgn',
	'/path/to/chess/white-sicilian-defence.pgn',
]
BLACK_FILES = ['/path/to/chess/black-open.pgn']

ALL_NOTETYPES = [
	{ 'id': 111111, 'name': 'Basic' },
	{ 'id': 222222, 'name': 'Einfach' },
	{ 'id': 333333, 'name': 'Custom' },
]

BASIC_NAMES = {
	'en-US': 'Basic',
	'de': 'Einfach',
	'fr': 'Basic',
}

default_config = {
	'version': None,
	'colour': 'white',
	'decks': {
		'white': None,
		'black': None,
	},
	'imports': {},
	# This is the id of the notetype "Einfach", the German version of "Basic".
	'notetype': '222222',
}


class TestUpdate(unittest.TestCase):
	def __init__(self, methodName):
		super().__init__(methodName=methodName)

		self.mw_mock = MagicMock()
		self._setup_decks_mock(self.mw_mock)

	def _setup_decks_mock(self, mock):
		def id_for_name(*args, **kwargs):
			if args[0] == WHITE_DECK_NAME:
				return WHITE_DECK_ID
			elif args[0] == BLACK_DECK_NAME:
				return BLACK_DECK_ID
			else:
				return None

		mock.col.decks.id_for_name.side_effect = id_for_name

	@patch('src.updater.basic_names', BASIC_NAMES)
	def test_update_no_config(self):
		version = '1.2.3'
		updater = Updater(self.mw_mock, version)
		self.assertEqual([], updater._basic_names())
		wanted = copy.deepcopy(default_config)
		wanted['version'] = version

		got = updater.update_config(None)
		self.assertDictEqual(wanted, got)

	# @patch('src.updater.basic_names', BASIC_NAMES)
	# def test_update_old_default_config(self):
	# 	version = '1.2.3'
	# 	updater = Updater(self.mw_mock, version)
	# 	wanted = copy.deepcopy(default_config)
	# 	wanted['version'] = version
	# 	old_config = {
	# 		'colour': 'white',
	# 		'decks': {
	# 			'white': None,
	# 			'black': None,
	# 		},
	# 		'files': {
	# 			'white': [],
	# 			'black': [],
	# 		},
	# 		'notetype': 'Einfach'
	# 	}

	# 	got = updater.update_config(old_config)
	# 	self.assertDictEqual(wanted, got)

	# @patch('src.updater.basic_names', BASIC_NAMES)
	# def test_update_old_filled_config(self):
	# 	version = '1.2.3'
	# 	updater = Updater(self.mw_mock, version)
	# 	wanted = {
	# 		'version': version,
	# 		'colour': 'white',
	# 		'decks': {
	# 			'white': WHITE_DECK_ID,
	# 			'black': BLACK_DECK_ID,
	# 		},
	# 		'imports': {
	# 			f'{WHITE_DECK_ID}': {
	# 				'colour': 'white',
	# 				'files': WHITE_FILES,
	# 			},
	# 			f'{BLACK_DECK_ID}': {
	# 				'colour': 'black',
	# 				'files': BLACK_FILES,
	# 			},
	# 		},
	# 		'notetype': 'Einfach',
	# 	}
	# 	old_config = {
	# 		'colour': 'white',
	# 		'decks': {
	# 			'white': WHITE_DECK_NAME,
	# 			'black': BLACK_DECK_NAME,
	# 		},
	# 		'files': {
	# 			'white': WHITE_FILES,
	# 			'black': BLACK_FILES,
	# 		},
	# 		'notetype': 'Einfach'
	# 	}

	# 	self.maxDiff = None
	# 	got = updater.update_config(old_config)
	# 	self.assertDictEqual(wanted, got)
