from collections import deque
from typing import Iterator

import chess
from chess import Color
from chess.pgn import Game, GameNode

from utils import normalise_fen


class CardGenerator:
	def __init__(self, game: Game, colour: Color) -> None:
		self._game = game
		self._colour = colour
		self._node_fens: dict[GameNode, str] = {}
		self._questions: dict[str, list[GameNode]] = {}

		queue: deque[tuple[GameNode, GameNode | None]] = deque([(self._game, None)])

		# This lookup table stores all nodes from where a certain position can
		# be reached.
		self._parent_tree: dict[str, list[GameNode]] = {}

		while queue:
			node, parent = queue.popleft()
			board = node.board()
			norm_fen = normalise_fen(board.fen())
			self._node_fens[node] = norm_fen

			if parent is not None:
				self._parent_tree.setdefault(norm_fen, []).append(parent)

			if board.turn == self._colour and node.variations:
				self._questions.setdefault(norm_fen, []).append(node)

			for child in node.variations:
				queue.append((child, node))

	def cards(self) -> Iterator[tuple[str, Game]]:
		for fen, question_nodes in self._questions.items():
			if any(q_node.variations for q_node in question_nodes):
				yield fen, self._generate(question_nodes)

	def _generate(self, question_nodes: list[GameNode]) -> Game:
		# Pass 1: Find all parent nodes of every question node.
		queue: deque[GameNode] = deque(question_nodes)
		nodes: set[GameNode] = set(question_nodes)

		while queue:
			node = queue.popleft()
			fen = self._node_fens.get(node) or normalise_fen(node.board().fen())

			if fen in self._parent_tree:
				for parent in self._parent_tree[fen]:
					if parent not in nodes:
						nodes.add(parent)
						queue.append(parent)

		# Pass 2: Create the game subset.
		root_fen = self._game.board().fen()
		game = (
			Game()
			if root_fen == chess.STARTING_FEN
			else Game(
				{
					'SetUp': '1',
					'FEN': root_fen,
				}
			)
		)

		# Now recursively copy the original game with all comments and NAGs,
		# but only if it is contained in nodes.
		def _copy_subtree(source: GameNode, target: GameNode) -> None:
			for variation in source.variations:
				if variation not in nodes or variation.move is None:
					continue

				child = target.add_variation(
					variation.move,
					comment=variation.comment,
					starting_comment=variation.starting_comment,
					nags=set(variation.nags),
				)
				_copy_subtree(variation, child)

		_copy_subtree(self._game, game)

		# Now add all variations from all question nodes as answers on the leaf.
		leaf = game
		while leaf.variations:
			leaf = leaf.variations[0]

		seen_moves: set[chess.Move] = set()
		for q_node in question_nodes:
			for variation in q_node.variations:
				if variation.move is None or variation.move in seen_moves:
					continue

				seen_moves.add(variation.move)
				leaf.add_variation(
					variation.move,
					comment=variation.comment,
					starting_comment=variation.starting_comment,
					nags=set(variation.nags),
				)

		return game
