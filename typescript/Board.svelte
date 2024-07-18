<script lang="ts">
	import { onDestroy } from 'svelte';
	import { ChessgroundUnstyled as Chessground } from 'svelte-chessground';
	import { configuration } from './store';

	let initialized = false;
	let classes: Array<string> = ['loading'];

	const unsubscribe = configuration.subscribe(config => {
		if (!config) {
			return;
		}

		initialized = true;

		classes = [];
		if (config.board['3D']) {
			classes.push('is3d');
		} else {
			classes.push('is2d');
			classes.push('cot-board-' + config.board['2Dboard']);
		}
	});

	onDestroy(() => {
		unsubscribe();
	});
</script>

<chess-board class={classes.join(' ')}>
	<Chessground />
</chess-board>

<style>
	chess-board.loading {
		visibility: hidden;
	}
</style>
