import unittest
import copy
import semantic_version as sv
from unittest.mock import MagicMock, patch
from src.updater import Updater

WHITE_DECK_NAME = 'Chess::Opening::White'
BLACK_DECK_NAME = 'Chess::Opening::Black'

WHITE_DECK_ID = 123456789
BLACK_DECK_ID = 987654321

MOCK_NOTETYPE_ID = 222222

BASIC_NAMES = {
	'en-US': 'Basic',
	'de': 'Einfach',
	'fr': 'Basic',
}

# The target schema that the _fill_config pipeline produces for a fresh install.
EXPECTED_DEFAULT_CONFIG = {
	'version': sv.Version('1.2.3'),
	'colour': 'white',
	'decks': {
		'white': None,
		'black': None,
	},
	'imports': {},
	'notetype': MOCK_NOTETYPE_ID,
}


class TestUpdate(unittest.TestCase):
	def setUp(self):
		"""Sets up a clean, isolated mock of the Anki Main Window before each test."""
		self.mw_mock = MagicMock()
		self._setup_collection_mocks(self.mw_mock)

	def _setup_collection_mocks(self, mock_mw):
		def id_for_deck_name(name):
			if name == WHITE_DECK_NAME:
				return WHITE_DECK_ID
			elif name == BLACK_DECK_NAME:
				return BLACK_DECK_ID
			return None
		mock_mw.col.decks.id_for_name.side_effect = id_for_deck_name

		# Default empty loop return for card search sequences.
		mock_mw.col.decks.cids.return_value = []

		# Mock Model/Notetype ID lookups.
		def id_for_model_name(name):
			if name in BASIC_NAMES.values():
				return MOCK_NOTETYPE_ID
			return None
		mock_mw.col.models.id_for_name.side_effect = id_for_model_name

	@patch('src.updater.basic_names', BASIC_NAMES)
	@patch('anki.lang.current_lang', 'de')
	def test_update_fresh_install(self):
		"""Tests that an empty/missing configuration populates defaults successfully."""
		version = sv.Version('1.2.3')
		updater = Updater(version, self.mw_mock)

		# Expected output structure.
		wanted = copy.deepcopy(EXPECTED_DEFAULT_CONFIG)

		# Execute under None (or empty dict).
		got = updater.update_config(None)
		self.assertDictEqual(wanted, got)

	@patch('src.updater.basic_names', BASIC_NAMES)
	@patch('anki.lang.current_lang', 'en-US')
	def test_update_v0_legacy_migration(self):
		"""Tests that legacy layouts (< v1.0.0) migrate decks and files into structured entries."""
		version = sv.Version('1.2.3')
		updater = Updater(version, self.mw_mock)

		# Simulated legacy pre-1.0.0 configurations.
		legacy_config = {
			'version': '0.5.0',
			'decks': {
				'white': WHITE_DECK_NAME,
				'black': BLACK_DECK_NAME
			},
			'files': {
				'white': ['/path/to/white.pgn'],
				'black': ['/path/to/black.pgn']
			}
		}

		got = updater.update_config(legacy_config)

		# Assertions ensuring structural conversion took place.
		self.assertEqual(got['version'], version)
		self.assertEqual(got['decks']['white'], WHITE_DECK_ID)
		self.assertEqual(got['decks']['black'], BLACK_DECK_ID)

		self.assertIn(str(WHITE_DECK_ID), got['imports'])
		self.assertEqual(got['imports'][str(WHITE_DECK_ID)]['files'], ['/path/to/white.pgn'])
		self.assertNotIn('files', got)  # Top level 'files' key should be deleted

	@patch('src.updater.basic_names', BASIC_NAMES)
	@patch('anki.lang.current_lang', 'en-US')
	def test_update_no_op_when_versions_match(self):
		"""Tests that if the config version matches current, it bypasses migration steps entirely."""
		version = sv.Version('2.0.0')
		updater = Updater(version, self.mw_mock)

		matching_config = {
			'version': version,
			'colour': 'black',
			'decks': {'white': 111, 'black': 222},
			'imports': {},
			'notetype': MOCK_NOTETYPE_ID
		}

		# Stash copy to verify it didn't change mutate properties
		wanted = copy.deepcopy(matching_config)

		got = updater.update_config(matching_config)
		self.assertDictEqual(wanted, got)

	@patch('src.updater.basic_names', BASIC_NAMES)
	@patch('anki.lang.current_lang', 'en-US')
	def test_config_with_tag(self):
		"""Tests that config with tag field in imports validates and is preserved."""
		from jsonschema import validate
		from src.schema import schema

		version = sv.Version('1.2.3')
		updater = Updater(version, self.mw_mock)

		config = {
			'version': str(version),
			'colour': 'white',
			'decks': {'white': WHITE_DECK_ID, 'black': None},
			'imports': {
				str(WHITE_DECK_ID): {
					'colour': 'white',
					'files': ['/path/to/italian.pgn'],
					'tag': 'italian_game'
				}
			},
			'notetype': MOCK_NOTETYPE_ID
		}

		# Verify it passes jsonschema validation
		validate(config, schema=schema)

		got = updater.update_config(config)
		self.assertEqual(got['imports'][str(WHITE_DECK_ID)]['tag'], 'italian_game')

if __name__ == '__main__':
	unittest.main()
