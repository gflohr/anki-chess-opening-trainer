from collections import deque
from typing import Iterator

import chess
from chess import Color
from chess.pgn import Game, GameNode

from utils import normalise_fen


# The card generator does not convert arbitrary games into cards but only
# games that were created by our PGN collector. This rules out a lot of
# edge cases.
class CardGenerator:
	def __init__(self, game: Game, colour: Color) -> None:
		self._game = game
		self._colour = colour
		self._node_fens: dict[GameNode, str] = {}
		self._questions: dict[str, GameNode] = {}

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

			if (
				board.turn == self._colour
				and node.variations
				and norm_fen not in self._questions
			):
				if node.variations:
					self._questions[norm_fen] = node

			for child in node.variations:
				queue.append((child, node))

	def cards(self) -> Iterator[tuple[str, Game]]:
		# First create a lookup table for the parent relationships.
		for fen, node in self._questions.items():
			yield fen, self._generate(node)

	def _generate(self, question_node: GameNode) -> Game:
		# Pass 1: Find all parent nodes of the current one.
		queue: deque[GameNode] = deque([question_node])
		nodes: set[GameNode] = {question_node}

		while queue:
			node = queue.popleft()
			fen = self._node_fens.get(node) or normalise_fen(node.board().fen())

			if fen in self._parent_tree:
				for parent in self._parent_tree[fen]:
					for child in parent.variations:
						if self._node_fens.get(child) == fen and child not in nodes:
							nodes.add(child)

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

		# Now add all variations of question_node as answers.
		node = game
		while node.variations:
			node = node.variations[0]

		for variation in question_node.variations:
			node.add_variation(
				variation.move,
				comment=variation.comment,
				starting_comment=variation.starting_comment,
				nags=set(variation.nags),
			)

		return game
