<script lang="ts">
	import Header from './components/Header.svelte';
	import Moves from './components/Moves.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import type { Card } from './domain/card.js';
    import type { GameNode } from './domain/types';

	let { card = {} }: { card?: Partial<Card> } = $props();


	let movesComponent: Moves;

	// Theme state lives here, bound to the Header component.
	let isLight = $state(false);
	let isBoardHidden = $state(false);
	let canGoBackwards = $state(true);
	let canGoForward = $state(true);

	let selectedBoardId = $state<number | null>(null);
	let boardImg = $derived.by(() => {
		if (selectedBoardId === null) {
			if (card.isQuestion) {
				let node: GameNode | undefined = card.session?.game.questionMoves[0];
				if (!node) return card.images?.[0] as string;

				while(node) {
					if (!node[0].next) return card.images?.[node[0].id];
					node = card.session?.game.questionMoves[node[0].next];
				}
			} else {
				return card.images?.[card.session?.game.answerMoves[0].id as number]
			}

			return card.images?.[0];
		}

		return card.images?.[selectedBoardId];
	});

	let analyseLink = $derived.by(() => {
		if (card.isQuestion) return null;

		if (card.session?.game?.pgn) {
			return `https://lichess.org/analysis/pgn/${card.session.game.pgn}`;
		} else {
			return null;
		}
	})

	// Apply the theme attribute to the body whenever `isLight` changes.
	$effect(() => {
		document.documentElement.setAttribute('data-theme', isLight ? 'light' : 'dark');
	});
</script>

<Header
	bind:isLight
	bind:analyseLink
/>

<!-- App Container -->
<main class="app-container">
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
			bind:this={movesComponent}
			bind:selectedBoardId
			bind:canGoBackwards
			bind:canGoForward
		/>
		<Toolbar
			bind:isBoardHidden
			{canGoBackwards}
			{canGoForward}
			onToggleBoard={() => isBoardHidden = !isBoardHidden}
			onNavigate={(action) => {
				switch (action) {
					case 'start':
						movesComponent.goToStart();
						break;
					case 'previous':
						movesComponent.previousMove();
						break;
					case 'next':
						movesComponent.nextMove();
						break;
					case 'end':
						movesComponent.goToEnd();
						break;
				}
			}}
		/>
	</section>

</main>
