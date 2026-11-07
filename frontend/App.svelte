<script lang="ts">
	import Header from './components/Header.svelte';
	import Moves from './components/Moves.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import type { Card } from './domain/card.js';
	import type { GameNode, GraphMove } from './domain/types';

	let { card = {} }: { card?: Partial<Card> } = $props();

	// Theme state lives here, bound to the Header component
	let isLight = $state(false);
	let isBoardHidden = $state(false);

	let boardImg = $derived(card.images?.answers?.[0] || '');
	let selectedBoardId = $state<number | null>(null);

	// Apply the theme attribute to the body whenever `isLight` changes.
	$effect(() => {
		document.documentElement.setAttribute('data-theme', isLight ? 'light' : 'dark');
	});

	function findQuestionMove(id: number): boolean {
		const game = card.session?.game;
		if (!game) return false;

		let node: GameNode | undefined = game.questionMoves[0];

		while (node) {
			const graphMove: GraphMove = node[0];

			if (graphMove.id === id) {
				return true;
			}

			node = graphMove.next
				? game.questionMoves[graphMove.next]
				: undefined;
		}

		return false;
	}
</script>

<Header bind:isLight />

<!-- App Container -->
<main class="app-container">
	<p>Selected board id: {selectedBoardId}</p>
	<p>
		Is question move: {selectedBoardId !== null && findQuestionMove(selectedBoardId)}
	</p>

	<!-- Chessboard Display Section -->
	<section class="board-section">
		{#if !isBoardHidden}
			<div class="board-wrapper">
				<div id="board" class="chessboard-wrapper">
					<img src={boardImg} alt="Chessboard" />
				</div>
			</div>
		{:else}
			<div class="board-hidden-placeholder"></div>
		{/if}
	</section>

	<section class="moves-section">
		<Moves
			pcard={card}
			bind:selectedBoardId
		/>
		<Toolbar
			bind:isBoardHidden
			onToggleBoard={() => isBoardHidden = !isBoardHidden}
		/>
	</section>

</main>
