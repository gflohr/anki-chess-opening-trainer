import type { GameGraph, GameNode, GraphMove, Move } from './types';

export interface NavLookup {
	prev: number | null;
	next: number | null;
}

export interface MoveCell extends Move {
	clickable?: boolean;
	active?: boolean;
}

export interface MoveRow {
	moveNumber: number | null;
	white?: MoveCell;
	black?: MoveCell;
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

	/**
	 * Group played history moves into pairs of (White, Black) rows.
	 */
	generateMoveRows(
		selectedBoardId: number | null,
		images?: string[],
		answerMoves?: GraphMove[],
	) {
		const rows: MoveRow[] = [];

		// Add question moves.
		let node: GameNode | undefined = this.graph[0];
		let isWhite = true;
		let moveNumber = 1;
		let currentRow: MoveRow | undefined;

		while (node) {
			if (!currentRow) {
				currentRow = {
					moveNumber,
				};
			}
			const graphMove: GraphMove = node[0]; // Main variation.

			const move: MoveCell = {
				id: graphMove.id,
				san: graphMove.san,
			};

			if (isWhite) {
				currentRow.white = move;
			} else {
				currentRow.black = move;

				rows.push(currentRow);
				currentRow = undefined;
				++moveNumber;
			}

			isWhite = !isWhite;
			if (graphMove.next) {
				node = this.graph[graphMove.next];
			} else {
				node = undefined;
			}
		}

		if (answerMoves) {
			for (const move of answerMoves) {
				if (!currentRow) {
					currentRow = {
						moveNumber,
					};
				}

				const moveCell: MoveCell = {
					id: move.id,
					san: move.san,
					// Answer moves are clickable as long as they aren't already active
					clickable: true,
					status: 'correct',
				};

				if (isWhite) {
					currentRow.white = moveCell;
				} else {
					currentRow.black = moveCell;
				}

				rows.push(currentRow);
				currentRow = undefined;
			}
		}

		if (currentRow) {
			rows.push(currentRow);
		}

		// Set clickable property.
		for (const row of rows) {
			if (row.white) {
				const id = row.white.id;
				if (!row.white.active && images && images[id] !== '') {
					row.white.clickable = true;
				}
			}
			if (row.black) {
				const id = row.black.id;
				if (!row.black.active && images && images[id] !== '') {
					row.black.clickable = true;
				}
			}
		}

		const activeId = selectedBoardId ??
			answerMoves?.[0].id
			?? this.findLeaf()?.id;
		if (typeof activeId !== 'undefined') {
			for (const row of rows) {
				if (row.white?.id === activeId) {
					row.white.active = true;
					row.white.clickable = false;
					break;
				}
				if (row.black?.id === activeId) {
					row.black.active = true;
					row.black.clickable = false;
					break;
				}
			}
		}

		return rows;
	}
}
