from pathlib import Path

import chess
import chess.pgn
import pytest

from src.pgn_import.collector import Collector
from src.pgn_import.visitor import Visitor


def describe_basic_functionality() -> None:

	def it_should_initialise_with_an_empty_games_dictionary() -> None:
		"""Test that the Collector initializes with an empty games dictionary."""
		collector = Collector(colour=chess.WHITE)

		assert isinstance(collector.games(), dict)
		assert len(collector.games()) == 0

	def it_should_load_a_simple_pgn() -> None:
		fixture_path = Path(__file__).parent.parent / 'fixtures' / 'simple.pgn'
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(colour=chess.WHITE)

		with open(fixture_path, 'r', encoding='utf-8') as f:
			game_count = 0
			while True:
				game = chess.pgn.read_game(f)
				if game is None:
					break

				collector.add_game(game.board())
				game_count += 1

			assert game_count == 3
			assert len(collector.games()) == 2

	def it_should_set_the_colour_headers() -> None:
		"""Test that Collector properly sets colour headers for a Black repertoire deck."""
		collector = Collector(colour=chess.BLACK)

		collector.add_game(chess.Board())
		games = collector.games()

		assert len(games) == 1
		collected_game = list(games.values())[0]
		assert collected_game.headers['Colour'] == 'Black'

	def it_should_handle_custom_start_positions() -> None:
		"""Test that Collector correctly handles custom non-standard starting positions and move numbers."""
		collector = Collector(colour=chess.WHITE)

		# Custom position after 1. e4 e5 (Fullmove 2)
		custom_fen = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/5PPP/RNBQKBNR w KQkq - 0 2'
		collector.add_game(chess.Board(custom_fen))

		games = collector.games()
		assert len(games) == 1

		# Verify that the reconstructed key contains the correct minimum move number (2)
		key = list(games.keys())[0]
		assert key.endswith(' 0 2')

		# Verify that the stored game has the appropriate Setup and FEN headers set
		stored_game = games[key]
		assert stored_game.headers['SetUp'] == '1'
		assert stored_game.headers['FEN'] == custom_fen
		assert stored_game.board().fullmove_number == 2


def describe_london_system_variations():

	@pytest.fixture
	def collector() -> Collector:
		"""Fixture that loads london-variations.pgn and parses it into a collector."""
		fixture_path = (
			Path(__file__).parent.parent / 'fixtures' / 'london-variations.pgn'
		)
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(colour=chess.WHITE)

		with open(fixture_path, 'r', encoding='utf-8') as study_pgn:
			game_count = 0

			visitor = Visitor(collector)

			def get_visitor() -> chess.pgn.BaseVisitor:
				return visitor

			while chess.pgn.read_game(study_pgn, Visitor=get_visitor) is not None:
				game_count += 1

			# Assert that two games were processed.
			assert game_count == 2

		return collector

	def it_should_aggregate_into_a_single_game(collector: Collector) -> None:
		games = collector.games()
		assert len(games) == 1

	def it_should_contain_expected_moves(collector: Collector) -> None:
		games = collector.games()
		game = list(games.values())[0]
		# Add your specific move/node assertions on the shared game here
		assert game.headers.get('Colour') == 'White'


def describe_comment_handling():

	@pytest.fixture
	def collector() -> Collector:
		"""Fixture that loads comments.pgn and parses it into a collector."""
		fixture_path = Path(__file__).parent.parent / 'fixtures' / 'comments.pgn'
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(colour=chess.WHITE)

		with open(fixture_path, 'r', encoding='utf-8') as study_pgn:
			visitor = Visitor(collector)

			def get_visitor() -> chess.pgn.BaseVisitor:
				return visitor

			while chess.pgn.read_game(study_pgn, Visitor=get_visitor) is not None:
				pass

		return collector

	def it_should_add_move_comments(collector: Collector):
		games = collector.games()
		assert (len(games)) == 1

		game = list(games.values())[0]
		assert game.variations

		node = game.variation(0)
		node.comment

		assert node.comment == 'Open Game.'

	def it_should_merge_move_comments(collector: Collector):
		games = collector.games()
		assert (len(games)) == 1

		game = list(games.values())[0]

		# Traverse the mainline down to ply 2 (1... e5)
		node = game
		for _ in range(2):
			assert node.variations, 'Expected a move variation at this ply.'
			node = node.variation(0)

		assert node.comment == "Black mirror's White's move.{}Controls the centre."

	def it_should_discard_duplicate_comments(collector: Collector):
		games = collector.games()
		assert (len(games)) == 1

		game = list(games.values())[0]

		# Traverse the mainline down to ply 3 (2. Nf3)
		node = game
		for _ in range(3):
			assert node.variations, 'Expected a move variation at this ply.'
			node = node.variation(0)

		assert node.comment == "Attacks black's pawn."
