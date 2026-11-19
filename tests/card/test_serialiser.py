from chess.pgn import Game
import pytest

from src.card.serialiser import GameDump, Serialiser


def describe_game_serialising():
	def describe_standard_game():

		@pytest.fixture
		def game_dump() -> GameDump:
			game = Game()
			serialiser = Serialiser()
			return serialiser.serialise(game)

		def it_should_not_have_a_start_position(game_dump: GameDump):
			assert 'f' not in game_dump

	def describe_custom_game():
		fen = 'rnbqkbnr/ppp1pppp/8/3p4/3P1B2/8/PPP1PPPP/RN1QKBNR w KQkq - 0 1'

		@pytest.fixture
		def game_dump() -> GameDump:
			game = Game({
				'SetUp': '1',
				'FEN': fen
			})
			serialiser = Serialiser()
			return serialiser.serialise(game)

		def it_should_have_a_start_position(game_dump: GameDump):
			assert 'f' in game_dump
			assert game_dump['f'] == fen
