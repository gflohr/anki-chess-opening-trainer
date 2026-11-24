from pathlib import Path

import chess
from chess.pgn import Game

from src.card.generator import CardGenerator


def describe_card_generator():
	fixture_path = Path(__file__).parent.parent / 'fixtures' / 'open-variations.pgn'
	assert fixture_path.exists(), f'Fixture not found at {fixture_path}'

	with open(fixture_path, 'r', encoding='utf-8') as f:
		game = chess.pgn.read_game(f)

		assert game is not None

		# We expect the following cards to be created:
		#
		# Q: Start A: 1. e4, 1. Nf3
		# Q: 1. e4 e5 A: 2. Nf3
		# Q: 1. Nf3 Nc6 A: 2. e4
		# Q: 1. e4 e5 2. Nf3 Nc6 3. Bc4
		# Q: 1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 A: 3. c3
		# Q: 1. e4 e5 2. Nf3 Nc6 2. Bc4 Nf6 A: 3. Ng5
		generator = CardGenerator(game, chess.WHITE)

		for fen, node in generator.cards():
			moves = []
			for variation in node.variations:
				moves.append(variation.move.uci())

			print(f'FEN: {fen} | Answers: {moves}')
