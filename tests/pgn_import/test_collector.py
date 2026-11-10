from pathlib import Path
import chess
import chess.pgn
from src.pgn_import.collector import Collector


def test_collector_initialization() -> None:
	'''Test that the Collector initializes with an empty games dictionary.'''
	collector = Collector(colour=chess.WHITE)

	assert isinstance(collector.games(), dict)
	assert len(collector.games()) == 0


def test_collector_loads_simple_pgn() -> None:
	fixture_path = Path(__file__).parent.parent / 'fixtures' / 'simple.pgn'
	assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

	collector = Collector(colour=chess.WHITE)

	with open(fixture_path, 'r', encoding='utf-8') as f:
		game_count = 0
		while True:
			game = chess.pgn.read_game(f)
			if game is None:
				break

			collector.add_game(game.board().fen())
			game_count += 1

		assert game_count == 3
		assert len(collector.games()) == 2


def test_collector_black_deck() -> None:
	'''Test that Collector properly sets colour headers for a Black repertoire deck.'''
	collector = Collector(colour=chess.BLACK)

	collector.add_game(chess.STARTING_FEN)
	games = collector.games()

	assert len(games) == 1
	collected_game = list(games.values())[0]
	assert collected_game.headers['Colour'] == 'Black'


def test_collector_custom_starting_position() -> None:
	'''Test that Collector correctly handles custom non-standard starting positions and move numbers.'''
	collector = Collector(colour=chess.WHITE)

	# Custom position after 1. e4 e5 (Fullmove 2)
	custom_fen = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/5PPP/RNBQKBNR w KQkq - 0 2'
	game_id = collector.add_game(custom_fen)

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
