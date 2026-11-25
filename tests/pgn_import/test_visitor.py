from unittest.mock import MagicMock

import chess
from chess.pgn import SKIP

from pgn_import.visitor import Visitor


def describe_basic_functionality():

	def visitor_adds_games_to_collector() -> None:
		collector = MagicMock()

		visitor = Visitor(collector)

		board = chess.Board()
		board.push_san('d4')
		board.push_san('d5')

		visitor.begin_game()
		visitor.visit_board(board)

		collector.add_game.assert_called_once_with(board)

	def visitor_collects_and_returns_errors() -> None:
		collector = MagicMock()
		visitor = Visitor(collector)
		visitor._gameno = 2

		# Act
		visitor.handle_error(ValueError('Invalid PGN syntax'))
		res = visitor.result()

		# Assert output behavior
		assert res == [{'gameno': 2, 'error': 'Invalid PGN syntax'}]

	def visitor_adds_moves() -> None:
		collector = MagicMock()

		game_id = 'some game id'
		collector.add_game.return_value = game_id
		visitor = Visitor(collector)

		board = chess.Board()
		initial = board.fen()
		visitor.visit_board(board)

		collector.add_game.assert_called_once_with(board)

		new_game_id = 'the new game id'
		collector.add_move.return_value = new_game_id

		move = chess.Move.from_uci('d2d4')
		visitor.visit_move(board, move)
		board.push(move)
		after_white = board.fen()
		visitor.visit_board(board)

		collector.add_move.assert_called_once_with(
			move=move, fen_before=initial, fen_after=after_white
		)

		collector.add_move.reset_mock()

		move = chess.Move.from_uci('d7d5')
		visitor.visit_move(board, move)
		board.push(move)
		after_black = board.fen()
		visitor.visit_board(board)

		collector.add_move.assert_called_once_with(
			move=move,
			fen_before=after_white,
			fen_after=after_black,
		)


def describe_variation_skipping():
	def skips_white_variations_when_requested() -> None:
		collector = MagicMock()
		visitor = Visitor(
			collector, drop_white_variations=True, drop_black_variations=False
		)

		board = chess.Board()
		board.push_uci('d2d4')

		visitor.visit_board(board)
		result = visitor.begin_variation()

		assert result == SKIP

	def skips_black_variations_when_requested() -> None:
		collector = MagicMock()
		visitor = Visitor(
			collector, drop_white_variations=False, drop_black_variations=True
		)

		board = chess.Board()
		board.push_uci('d2d4')
		board.push_uci('d7d5')

		visitor.visit_board(board)
		result = visitor.begin_variation()

		assert result == SKIP

	def skips_not_white_variations_by_default() -> None:
		collector = MagicMock()
		visitor = Visitor(collector, drop_black_variations=True)

		board = chess.Board()
		board.push_uci('d2d4')

		visitor.visit_board(board)
		result = visitor.begin_variation()

		assert result != SKIP

	def skips_not_black_variations_by_default() -> None:
		collector = MagicMock()
		visitor = Visitor(collector, drop_white_variations=True)

		board = chess.Board()
		board.push_uci('d2d4')
		board.push_uci('d7d5')

		visitor.visit_board(board)

		result = visitor.begin_variation()

		assert result != SKIP

	def skips_no_white_variations_by_default() -> None:
		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		board.push_uci('d2d4')

		visitor.visit_board(board)
		result = visitor.begin_variation()

		assert result != SKIP

	def skips_no_black_variations_by_default() -> None:
		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		board.push_uci('d2d4')
		board.push_uci('d7d5')

		visitor.visit_board(board)
		result = visitor.begin_variation()

		assert result != SKIP


def describe_comments_nags():
	def it_should_add_move_comments() -> None:

		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		visitor.begin_game()

		visitor.visit_board(board)
		board.push_uci('d2d4')
		visitor.visit_move(board, chess.Move.from_uci('d2d4'))
		comment = "Queen's Pawn Opening"
		visitor.visit_comment(comment)

		collector.add_comment.assert_called_once_with(comment)

	def it_should_add_nags() -> None:

		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		visitor.begin_game()

		visitor.visit_board(board)
		board.push_uci('d2d4')
		visitor.visit_move(board, chess.Move.from_uci('d2d4'))
		nag = 1
		visitor.visit_nag(nag)

		collector.add_nag.assert_called_once_with(nag)

	def it_should_add_game_comments() -> None:

		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		visitor.begin_game()
		visitor.visit_board(board)
		comment = 'Open Game'
		visitor.visit_comment(comment)

		collector.add_variation_comment_called_once_with(comment)

	def it_should_add_variation_comments() -> None:

		collector = MagicMock()
		visitor = Visitor(collector)

		board = chess.Board()
		visitor.begin_game()
		visitor.visit_move(board, chess.Move.from_uci('d2d4'))
		board.push_uci('d2d4')
		visitor.visit_board(board)
		board.pop()
		visitor.begin_variation()
		comment = 'Open Game'
		visitor.visit_comment(comment)

		collector.add_variation_comment_called_once_with(comment)
