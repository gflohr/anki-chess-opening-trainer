import chess
from chess.pgn import Game

from utils import make_question

def describe_utility_functions():
	def describe_make_question():
		def it_should_strip_off_all_answer_and_comments_and_nags():
			game = Game()

			node = game.add_variation(chess.Move.from_uci('e2e4'))
			node = node.add_variation(chess.Move.from_uci('e7e5'))
			node = node.add_variation(chess.Move.from_uci('g1f3'))
			node = node.add_variation(chess.Move.from_uci('b8c6'))
			node = node.add_variation(chess.Move.from_uci('f1c4'))
			node = node.add_variation(chess.Move.from_uci('g8f6'))
			node.starting_comment = 'Two knights defence'
			node.comment = 'The most popular reaction is the fried-liver attach'
			node.nags.add(5)
			node.add_variation(chess.Move.from_uci('d2d3'))
			node.add_variation(chess.Move.from_uci('f3g5'))

			question = make_question(game)

			exporter = chess.pgn.StringExporter(
				headers=False, variations=True, comments=True
			)
			pgn_string = question.accept(exporter)

			assert pgn_string == '1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 *'

