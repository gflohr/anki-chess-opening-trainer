<script lang="ts">
	import { onDestroy } from 'svelte';
	import { ChessgroundUnstyled as Chessground } from 'svelte-chessground';
	import { configuration } from './store';

	let classes: Array<string> = ['loading'];

	const unsubscribe = configuration.subscribe(config => {
		if (!config) {
			return;
		}

		classes = [];
		if (config.board['3D']) {
			classes.push('is3d');
			classes.push('cot-board-' + config.board['3Dboard']);
			classes.push('pieces-' + config.board['3Dpieces']);
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
	<Chessground addPieceZIndex={true} />
</chess-board>

<style lang="scss">
chess-board {
	position: relative;

}

chess-board.loading {
	visibility: hidden;
}
</style>
