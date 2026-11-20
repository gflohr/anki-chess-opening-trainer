import chess
import pytest
from chess.pgn import Game

from src.card.serialiser import GameDump, CardSerialiser


def describe_game_serialising():
	def describe_standard_game():

		@pytest.fixture
		def game_dump() -> GameDump:
			game = Game()
			node = game.add_variation(chess.Move.from_uci('d2d4'))
			node = node.add_variation(chess.Move.from_uci('d7d5'))
			node = node.add_variation(chess.Move.from_uci('c1f4'))
			node.starting_comment = 'Should we play the Queen\'s Gambit?'
			node.comment = 'The London System'
			node.nags.add(1)
			node.nags.add(10)
			serialiser = CardSerialiser()

			return serialiser.serialise(game)

		def it_should_not_have_a_start_position(game_dump: GameDump):
			assert 'f' not in game_dump

		def it_should_have_a_first_move(game_dump: GameDump):
			assert 'v' in game_dump
			variations = game_dump['v']

			assert len(variations) == 1
			assert 'm' in variations[0]
			assert variations[0]['m'] == 'd2d4'

		def it_should_have_a_second_move(game_dump: GameDump):
			node = game_dump

			for _ in range(2):
				assert 'v' in node, 'Expected a move variation at this ply.'
				node = node['v'][0]

			assert 'm' in node
			assert node['m'] == 'd7d5'

		def it_should_have_nags_in_the_third_move(game_dump: GameDump):
			node = game_dump

			for _ in range(3):
				assert 'v' in node, 'Expected a move variation at this ply.'
				node = node['v'][0]

			assert 'm' in node
			assert node['m'] == 'c1f4'
			assert 'n' in node
			assert len(node['n']) == 2
			assert 1 in node['n']
			assert 10 in node['n']

	def describe_custom_game():
		fen = 'rnbqkbnr/ppp1pppp/8/3p4/3P1B2/8/PPP1PPPP/RN1QKBNR w KQkq - 0 1'

		@pytest.fixture
		def game_dump() -> GameDump:
			game = Game({'SetUp': '1', 'FEN': fen})
			serialiser = CardSerialiser()
			return serialiser.serialise(game)

		def it_should_have_a_start_position(game_dump: GameDump):
			assert 'f' in game_dump
			assert game_dump['f'] == fen
