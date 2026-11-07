<script lang="ts">
	import type { Card } from '../domain/card.js';
	import type { GameNode, GraphMove, Move } from '../domain/types.js';

	interface Props {
		pcard: Partial<Card>;
		selectedBoardId: number | null;
		canGoBackwards: boolean;
		canGoForward: boolean;
	}

	let {
		pcard,
		selectedBoardId = $bindable<number | null>(null),
		canGoBackwards = $bindable(true),
		canGoForward = $bindable(true),
	}: Props = $props();

	interface MoveCell extends Move {
		clickable?: boolean;
		active?: boolean;
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
			const isActive = selectedBoardId !== null
				? selectedBoardId === graphMove.id
				: (card.isQuestion && isLeaf);

			const move: MoveCell = {
				id: graphMove.id,
				san: graphMove.san,
				active: isActive,
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
				const isActive = selectedBoardId !== null
					? selectedBoardId === move.id
					: isFirst;

				const moveCell: MoveCell = {
					id: move.id,
					san: move.san,
					// Answer moves are clickable as long as they aren't already active
					clickable: !isActive,
					active: isActive,
					status: 'correct',
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

		// Set clickable property.
		for (const row of rows) {
			if (row.white) {
				const id = row.white.id;
				if (!row.white.active && card.images && card.images[id] !== '') {
					row.white.clickable = true;
				}
			}
			if (row.black) {
				const id = row.black.id;
				if (!row.black.active && card.images && card.images[id] !== '') {
					row.black.clickable = true;
				}
			}
		}

		return rows;
	});

	$effect(() => {
		rows;

		canGoBackwards = hasPreviousMove();
		canGoForward = hasNextMove();
	});

	$effect(() => {
		function handleKeydown(event: KeyboardEvent) {
			if (event.target instanceof HTMLInputElement ||
				event.target instanceof HTMLTextAreaElement) {
				return;
			}

			switch (event.key) {
				case 'ArrowLeft':
					if (canGoBackwards) previousMove();
					break;
				case 'ArrowRight':
					if (canGoForward) nextMove();
					break;
				case 'Home':
					goToStart();
					break;
				case 'End':
					goToEnd();
					break;
			}
		}

		window.addEventListener('keydown', handleKeydown);

		return () => window.removeEventListener('keydown', handleKeydown);
	});

	function handleCellClick(cell?: MoveCell) {
		if (!cell || !cell.clickable) return;
		selectedBoardId = cell.id;
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

	function findActiveRowIndex(): number | null {
		for (let i = 0; i < rows.length; ++i) {
			const row = rows[i];
			if (row.white?.active) {
				return i;
			}

			if (row.black?.active) {
				return i;
			}
		}

		return null;
	}

	function hasPreviousMove(): boolean {
		if (!rows) return false;

		const activeRowIndex = findActiveRowIndex();
		if (activeRowIndex === null) return false;

		return true;
	}

	function hasNextMove(): boolean {
		const rowIndex = findActiveRowIndex();

		if (rowIndex === null) {
			return !!rows.length;
		}

		if (rowIndex === rows.length - 1) {
			const lastRow = rows[rowIndex];
			if (lastRow.white?.active && lastRow.black) {
				return true;
			} else {
				return false;
			}
		} else {
			return true;
		}
	}

	export function previousMove() {
		let rowIndex = findActiveRowIndex();
		if (rowIndex === null) return; // Already at start.

		let isWhite: boolean;
		if (rows[rowIndex].black?.active) {
			rows[rowIndex].black!.active = false;
			isWhite = false;
		} else {
			rows[rowIndex].white!.active = false;
			isWhite = true;
		}

		while (rowIndex >= 0) {
			if (isWhite) {
				--rowIndex;
			}
			if (rowIndex < 0) {
				goToStart();
				return;
			}

			isWhite = !isWhite;

			const row = rows[rowIndex];
			const cell = isWhite ? row.white : row.black;
			if (cell) {
				selectedBoardId = cell.id;
				return;
			}
		}

		goToStart();
	}

	export function nextMove() {
		let rowIndex = findActiveRowIndex();
		const maxRowIndex = rows.length - 1;

		if (rowIndex === maxRowIndex) {
			goToEnd();
			return;
		}

		let isBlack: boolean;
		if (rowIndex === null) {
			rowIndex = -1;
			isBlack = true;
		} else if (rows[rowIndex].black?.active) {
			rows[rowIndex].black!.active = false;
			isBlack = true;
		} else {
			rows[rowIndex].white!.active = false;
			isBlack = false;
		}

		while (rowIndex < maxRowIndex) {
			if (isBlack) {
				++rowIndex;
			}
			if (rowIndex > maxRowIndex) break;

			isBlack = !isBlack;

			const row = rows[rowIndex];
			const cell = isBlack ? row.black : row.white;
			if (cell) {
				selectedBoardId = cell.id;
				return;
			}
		}

		goToEnd();
	}

	export function goToStart() {
		selectedBoardId = 0;
		canGoBackwards = false;
		canGoForward = hasNextMove();
	}

	export function goToEnd() {
		const row = rows[rows.length - 1];
		const cell = row.white ? row.white : row.black;

		selectedBoardId = cell!.id;
		canGoForward = false;
		canGoBackwards = hasPreviousMove();
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
