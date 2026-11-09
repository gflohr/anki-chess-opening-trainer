import type { GameGraph, GraphMove } from './types';

export interface NavLookup {
	prev: number | null;
	next: number | null;
}

export class GameGraphService {
	constructor(private readonly graph: GameGraph) {}

	findLeaf(): GraphMove | null {
		if (!this.graph.length) {
			return null;
		}

		let node = this.graph[0];
		while (node) {
			if (node[0].next) {
				node = this.graph[node[0].next];
			} else {
				if (node.length > 1) {
					throw new Error('Game graph has more than one leaf!');
				}

				return node[0];
			}
		}

		throw new Error('Could not find leaf in game graph.');
	}

	navigationLookup(answerMoves?: GraphMove[]) {
		const nodes = this.graph;

		// The indices are move IDs, not node ids!
		const lookups: NavLookup[] = [];

		// Board/Move id 0 is the initial position. It never has a previous
		// position.
		if (nodes.length) {
			lookups[0] = {
				prev: null,
				next: nodes[0]?.[0]?.id,
			};

			for (const move of nodes[0]) {
				lookups[move.id] = { prev: 0, next: null };
			}
		} else if (!answerMoves) {
			lookups[0] = {
				prev: null,
				next: null,
			}; // Nowhere to go to for a question.
		} else {
			const answerMoveId = answerMoves[0].id;
			lookups[0] = {
				prev: null,
				next: answerMoveId,
			};
			lookups[answerMoveId] = {
				prev: 0,
				next: null, // Will be filled later.
			};
		}

		// Build up the rest of the table.
		for (let n = 0; n < nodes.length; ++n) {
			const node = nodes[n];

			// The previous position is the same for all moves from this
			// node. It is always the main variation of the predecessor.
			for (const move of node) {
				lookups[move.id] ??= { prev: null, next: null };

				if (move.next) {
					const nextNode = nodes[move.next];
					lookups[move.id].next = nextNode[0].id;

					for (const nextMove of nextNode) {
						lookups[nextMove.id] ??= { prev: null, next: null };
						lookups[nextMove.id].prev = move.id;
					}
				} else if (answerMoves) {
					const answerMoveId = answerMoves[0].id;
					lookups[move.id].next = answerMoveId;

					lookups[answerMoveId] ??= { prev: null, next: null };
					lookups[answerMoveId].prev ??= move.id;
				}
			}
		}

		if (answerMoves) {
			for (let i = 0; i < answerMoves.length; ++i) {
				const move = answerMoves[i];
				lookups[move.id] ??= { prev: null, next: null };

				if (i > 0) {
					const prevMove = answerMoves[i - 1];
					lookups[move.id].prev = prevMove.id;
				}

				if (i < answerMoves.length - 1) {
					const nextMove = answerMoves[i + 1];
					lookups[move.id].next = nextMove.id;
				}
			}
		}

		return lookups;
	}
}
