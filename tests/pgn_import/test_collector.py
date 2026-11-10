from pathlib import Path
import chess.pgn
from src.pgn_import.collector import Collector


def test_collector_initialization() -> None:
	'''Test that the Collector initializes with an empty games dictionary.'''
	collector = Collector()

	assert isinstance(collector.games, dict)
	assert len(collector.games) == 0

def test_collector_loads_simple_pgn() -> None:
	# Resolve the path to the fixture relative to this test file
	fixture_path = Path(__file__).parent.parent / 'fixtures' / 'simple.pgn'

	assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

	collector = Collector()

	with open(fixture_path, 'r', encoding='utf-8') as f:
		game_count = 0
		while True:
			game = chess.pgn.read_game(f)
			if game is None:
				break

			collector.add_game(game)
			game_count += 1

		# The collectdion contains 3 games.
		assert game_count == 3

		# One has a redundant initial FEN (starting position).
		assert len(collector.games) == 2

def test_normalise_fen() -> None:
	collector = Collector()

	fen = 'rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq - 1 2'
	assert collector.normalise_fen(fen) == 'rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq -'
