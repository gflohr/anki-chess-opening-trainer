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
		# Collect nodes strictly after question_node so repeating positions
		# later in the game cannot be pulled into the pre-question history.
		descendants: set[GameNode] = set()
		desc_queue: deque[GameNode] = deque(question_node.variations)
		while desc_queue:
			curr = desc_queue.popleft()
			if curr not in descendants:
				descendants.add(curr)
				desc_queue.extend(curr.variations)

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
		copied_question: GameNode = game

		def _copy_history(source: GameNode, target: GameNode) -> None:
			nonlocal copied_question
			for variation in source.variations:
				if (
					variation not in nodes
					or variation in descendants
					or variation.move is None
				):
					continue

				child = target.add_variation(
					variation.move,
					comment=variation.comment,
					starting_comment=variation.starting_comment,
					nags=set(variation.nags),
				)
				if variation is question_node:
					copied_question = child
					# Do not copy question_node's own variations here; they are added as answers.
					continue
				_copy_history(variation, child)

		_copy_history(self._game, game)

		question_fen = self._node_fens[question_node]

		def _find_question_node(curr: GameNode) -> GameNode | None:
			if normalise_fen(curr.board().fen()) == question_fen:
				return curr
			for child in curr.variations:
				found = _find_question_node(child)
				if found is not None:
					return found
			return None

		target_question = _find_question_node(game) or game
		for variation in question_node.variations:
			if variation.move is not None and not target_question.has_variation(
				variation.move
			):
				target_question.add_variation(
					variation.move,
					comment=variation.comment,
					starting_comment=variation.starting_comment,
					nags=set(variation.nags),
				)

		return game
