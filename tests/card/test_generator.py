from pathlib import Path

import chess

from src.card.generator import CardGenerator
from src.pgn_import.collector import Collector
from src.pgn_import.visitor import Visitor


def describe_card_generator():
	def describe_open_variations():
		fixture_path = Path(__file__).parent.parent / 'fixtures' / 'open-variations.pgn'
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(chess.WHITE)
		visitor = Visitor(collector)

		with open(fixture_path, 'r', encoding='utf-8') as f:
			while True:
				errors = chess.pgn.read_game(f, Visitor=lambda: visitor)
				if errors is None:
					break
				assert len(errors) == 0

			games = collector.games()
			assert len(games) == 1

			game = next(iter(games.values()))

			generator = CardGenerator(game, chess.WHITE)

			cards = set([])
			for fen, game in generator.cards():
				exporter = chess.pgn.StringExporter(
					headers=False, variations=True, comments=True
				)
				pgn_string = game.accept(exporter)
				cards.add(pgn_string.replace('\n', ' '))

		def it_should_have_six_cards():
			assert len(cards) == 6

		def it_should_generate_the_correct_cards():
			assert '1. e4 ( 1. Nf3 ) *' in cards
			assert '1. e4 e5 2. Nf3 *' in cards
			assert '1. Nf3 Nc6 2. e4 *' in cards
			assert '1. e4 ( 1. Nf3 Nc6 2. e4 e5 ) 1... e5 2. Nf3 Nc6 3. Bc4 *' in cards
			assert (
				'1. e4 ( 1. Nf3 Nc6 2. e4 e5 ) 1... e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 { This is the classical variation. } *'
				in cards
			)
			assert (
				'1. e4 ( 1. Nf3 Nc6 2. e4 e5 ) 1... e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 $5 *'
				in cards
			)

	def describe_crossing_lines():
		fixture_path = Path(__file__).parent.parent / 'fixtures' / 'crossing-lines.pgn'
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(chess.WHITE)
		visitor = Visitor(collector)

		with open(fixture_path, 'r', encoding='utf-8') as f:
			while True:
				errors = chess.pgn.read_game(f, Visitor=lambda: visitor)
				if errors is None:
					break
				assert len(errors) == 0

			games = collector.games()
			assert len(games) == 1

			game = next(iter(games.values()))

			generator = CardGenerator(game, chess.WHITE)

			cards = set([])
			for fen, game in generator.cards():
				exporter = chess.pgn.StringExporter(
					headers=False, variations=True, comments=True
				)
				pgn_string = game.accept(exporter)
				cards.add(pgn_string.replace('\n', ' '))

		def it_should_have_four_cards():
			assert len(cards) == 4

		def it_should_generate_the_correct_cards():
			assert '1. e4 ( 1. Nf3 ) *' in cards
			assert '1. e4 e5 2. Nf3 *' in cards
			assert '1. Nf3 Nc6 2. e4 *' in cards
			assert (
				'1. e4 ( 1. Nf3 Nc6 2. e4 e5 ) 1... e5 2. Nf3 Nc6 3. Bc4 ( 3. d4 ) *'
				in cards
			)

	def describe_repetition():
		fixture_path = Path(__file__).parent.parent / 'fixtures' / 'repetition.pgn'
		assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

		collector = Collector(chess.WHITE)
		visitor = Visitor(collector)

		with open(fixture_path, 'r', encoding='utf-8') as f:
			while True:
				errors = chess.pgn.read_game(f, Visitor=lambda: visitor)
				if errors is None:
					break
				assert len(errors) == 0

			games = collector.games()
			assert len(games) == 1

			game = next(iter(games.values()))
			generator = CardGenerator(game, chess.WHITE)

			cards = set([])
			for fen, game in generator.cards():
				exporter = chess.pgn.StringExporter(
					headers=False, variations=True, comments=True
				)
				pgn_string = game.accept(exporter)
				cards.add(pgn_string.replace('\n', ' '))

		def it_should_have_two_cards():
			assert len(cards) == 2

		def it_should_generate_the_correct_cards():
			assert '1. Nf3 ( 1. e4 ) *' in cards
			assert '1. Nf3 Nf6 2. Ng1 *' in cards
