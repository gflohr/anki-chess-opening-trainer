<script lang="ts">
    import { rawCheck } from 'valibot';
	import type { Card } from '../domain/card.js';
    import { GameGraphService, type MoveCell, type MoveRow, type NavLookup } from '../domain/game-graph-service.js';
	import type { GameNode, GraphMove, Move } from '../domain/types.js';
    import { createDataTransfer } from '@testing-library/user-event/dist/cjs/utils/index.js';

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

	let graphService = $derived.by(() => {
		const card = pcard as Card;
		const game = card?.session?.game;
		return new GameGraphService(game.questionMoves ?? []);
    });

	/**
	 * Group played history moves into pairs of (White, Black) rows.
	 */
	let rows = $derived.by(() => {
		const card = pcard as Card;
		const rows = card.isQuestion
			? graphService.generateMoveRows(selectedBoardId, card.images)
			: graphService.generateMoveRows(selectedBoardId, card.images, card.session.game.answerMoves);

		return rows;
	});

	let navLookups = $derived.by(() => {
		const card = pcard as Card;

		if (card.isQuestion) {
			return graphService.navigationLookup();
		} else {
			return graphService.navigationLookup(card.session.game.answerMoves);
		}
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
					event.preventDefault();
					if (event.shiftKey) {
						if (canGoBackwards) goToStart();
					} else if (canGoBackwards) {
						previousMove();
					}
					break;

				case 'ArrowRight':
					event.preventDefault();
					if (event.shiftKey) {
						if (canGoForward) goToEnd();
					} else if (canGoForward) {
						nextMove();
					}
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

		selectMove(cell.id);
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

	function hasPreviousMove(): boolean {
		const card = pcard as Card;

		if (selectedBoardId === null) {
			if (card.isQuestion) {
				return !!card.session.game.questionMoves.length;
			} else {
				return true;
			}
		}

		if (navLookups[selectedBoardId].prev !== null) {
			return true;
		} else {
			return false;
		}
	}

	function hasNextMove(): boolean {
		const card = pcard as Card;

		if (selectedBoardId === null) {
			if (card.isQuestion) {
				return false;
			} else {
				return card.session.game.answerMoves.length > 0;
			}
		};

		if (navLookups[selectedBoardId].next !== null) {
			return true;
		} else {
			return false;
		}
	}

	function selectMove(id: number) {
		selectedBoardId = id;
	}

	function initialBoardId(): number | null {
		const card = pcard as Card;

		if (card.isQuestion) {
			return graphService.findLeaf()?.id ?? null;
		} else {
			return card.session.game.answerMoves[0].id;
		}
	}

	export function previousMove() {
		if (selectedBoardId === null) {
			selectedBoardId = initialBoardId();
			if (selectedBoardId === null) return;
		}

		selectedBoardId = navLookups[selectedBoardId].prev;
		if (selectedBoardId === null || navLookups[selectedBoardId].prev === null) {
			canGoBackwards = false;
		} else {
			canGoBackwards = true;
		}
	}

	export function nextMove() {
		if (selectedBoardId === null) {
			selectedBoardId = initialBoardId();
			if (selectedBoardId === null) return;
		}

		selectedBoardId = navLookups[selectedBoardId].next;
		if (selectedBoardId === null || navLookups[selectedBoardId].next === null) {
			canGoForward = false;
		} else {
			canGoForward = true;
		}
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
