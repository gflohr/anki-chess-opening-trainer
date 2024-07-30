<script lang="ts">
	import { onDestroy } from 'svelte';
	import Clock from './Clock.svelte';
	import Movelist from './Movelist.svelte';
	import { configuration } from './store';

	let classes: Array<string> = [];
	let displayClock = true;

	const unsubscribe = configuration.subscribe(config => {
		if (!config) {
			return;
		}

		classes = [];
		if (config.board['3D']) {
			classes.push('is3d');
		} else {
			classes.push('is2d');
		}

		displayClock = config.board.displayClock;
	});

	onDestroy(() => unsubscribe);
</script>

<chess-sidebar class={classes}>
	<Movelist></Movelist>
	{#if displayClock}
	<Clock></Clock>
	{/if}
</chess-sidebar>

<style lang="scss">
	chess-sidebar {
		display: grid;
		grid-template-columns: 1fr;
		grid-template-rows: max-content auto max-content;
	}
</style>
