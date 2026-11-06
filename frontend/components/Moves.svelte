<script lang="ts">
	import { CUID2_REGEX } from 'valibot';
	import type { Config } from '../config.js';
	import type { GameNode, GraphMove, Move } from '../domain/types.js';

	interface Props {
		config: Config;
	}

	let { config }: Props = $props();

	interface MoveCell extends Move {
		clickable?: boolean;
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
		const rows: MoveRow[] = [];

		// Add question moves.
		const game = config.session.game;
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

			const move: MoveCell = {
				id: graphMove.id,
				san: graphMove.san,
				status: graphMove.status,
				clickable: !graphMove.next,
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

		if (currentRow) {
			rows.push(currentRow);
		}

		return rows;
	});

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
						onclick={() => row.black}
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
