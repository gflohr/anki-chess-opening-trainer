<script lang="ts">
	import type { Card } from '../card.js';
	import type { GameNode, GraphMove, Move } from '../domain/types.js';

	interface Props {
		pcard: Partial<Card>;
	}

	let { pcard }: Props = $props();

	// Track manually clicked active cell ID (null means default initialization)
	let selectedId = $state<number | null>(null);

	interface MoveCell extends Move {
		clickable?: boolean;
		active?: boolean;
		image?: string;
	}

	interface MoveRow {
		moveNumber: number | null;
		white?: MoveCell;
		black?: MoveCell;
	}

	/**
	 * Group played history moves into pairs of (White, Black) rows.
	 */
	let rows = $derived.by(() => {
		const card = pcard as Card;
		const rows: MoveRow[] = [];

		// Add question moves.
		const game = card.session.game;
		let node: GameNode | undefined = game.questionMoves[0];
		let isWhite = true;
		let moveNumber = 1;
		let currentRow: MoveRow | undefined;

		while(node) {
			if (!currentRow) {
				currentRow = {
					moveNumber,
				};
			}
			const graphMove: GraphMove = node[0]; // Main variation.
			const isLeaf = !graphMove.next;

			// Determine if this cell is active
			const isActive = selectedId !== null
				? selectedId === graphMove.id
				: (card.isQuestion && isLeaf);

			const move: MoveCell = {
				id: graphMove.id,
				san: graphMove.san,
				// A move is only clickable if it's a leaf node AND it is NOT currently active
				clickable: isLeaf && !isActive,
				active: isActive,
			};

			if (isLeaf) {
				move.image = card.images?.question;
			}

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
				node = game.questionMoves[graphMove.next];
			} else {
				node = undefined;
			}
		}

		if (!card.isQuestion) {
			let count = 0;
			for (const move of card.session.game.answerMoves) {
				if (!currentRow) {
					currentRow = {
						moveNumber,
					};
				}

				const isFirst = count === 0;
				const isActive = selectedId !== null
					? selectedId === move.id
					: isFirst;

				const image = card.images?.answers[count];
				const moveCell: MoveCell = {
					id: move.id,
					san: move.san,
					// Answer moves are clickable as long as they aren't already active
					clickable: !isActive,
					active: isActive,
					status: 'correct',
					image,
				};

				if (isWhite) {
					currentRow.white = moveCell;
				} else {
					currentRow.black = moveCell;
				}

				rows.push(currentRow);
				currentRow = undefined;
				count++;
			}
		}

		if (currentRow) {
			rows.push(currentRow);
		}

		return rows;
	});

	function handleCellClick(cell?: MoveCell) {
		if (!cell || !cell.clickable) return;
		selectedId = cell.id;
	}

	/**
	 * Helper to determine Bootstrap icon class based on move status.
	 */
	function getStatusIcon(status?: Move['status']): string | null {
		switch (status) {
			case 'correct':
				return 'bi-check-circle-fill';
			case 'wrong':
				return 'bi-x-circle-fill';
			case 'missing':
				return 'bi-exclamation-circle-fill';
			default:
				return null;
		}
	}
</script>

<div class="history-container">
	<table class="move-table">
		<tbody>
			{#each rows as row}
				<tr>
					<td class="col-num">{row.moveNumber ?? ''}</td>

					<!-- White Move Cell -->
					<td
						class="col-white"
						class:clickable={row.white?.clickable}
						class:active-move={row.white?.active}
						onclick={() => handleCellClick(row.white)}
					>
						{#if row.white}
							<span class="move-cell" class:correct={row.white.status === 'correct'} class:wrong={row.white.status === 'wrong'} class:missing={row.white.status === 'missing'}>
								{row.white.san}
								{#if getStatusIcon(row.white.status)}
									<i class="bi {getStatusIcon(row.white.status)}"></i>
								{/if}
							</span>
						{/if}
					</td>

					<!-- Black Move Cell -->
					<td
						class="col-black"
						class:clickable={row.black?.clickable}
						class:active-move={row.black?.active}
						onclick={() => handleCellClick(row.black)}
					>
						{#if row.black}
							<span class="move-cell" class:correct={row.black.status === 'correct'} class:wrong={row.black.status === 'wrong'} class:missing={row.black.status === 'missing'}>
								{row.black.san}
								{#if getStatusIcon(row.black.status)}
									<i class="bi {getStatusIcon(row.black.status)}"></i>
								{/if}
							</span>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
