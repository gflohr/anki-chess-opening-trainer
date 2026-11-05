<script lang="ts">
	import Header from './components/Header.svelte';
	import Moves from './components/Moves.svelte';
	import Toolbar from './components/Toolbar.svelte';
	import type { Config } from './config.js';

	let { config = {} }: { config?: Partial<Config> } = $props();

	// Theme state lives here, bound to the Header component
	let isLight = $state(false);
	let isBoardHidden = $state(false);

	//let questionImg = $derived(config.images?.question || '');
	let answerImg = $derived(config.images?.answers?.[0] || '');

	// Apply the theme attribute to the body whenever `isLight` changes
	$effect(() => {
		document.body.setAttribute('data-theme', isLight ? 'light' : 'dark');
	});
</script>

<Header bind:isLight />

<!-- App Container -->
<main class="app-container">

	<!-- Chessboard Display Section -->
	<section class="board-section">
		{#if !isBoardHidden}
			<div class="board-wrapper">
				<div id="board" class="chessboard-wrapper">
					<img src={answerImg} alt="Chessboard" />
				</div>
			</div>
		{:else}
			<div class="board-hidden-placeholder"></div>
		{/if}
	</section>

	<section class="moves-section">
		<Moves />
		<Toolbar
			bind:isBoardHidden
			onToggleBoard={() => isBoardHidden = !isBoardHidden}
		/>
	</section>

</main>
