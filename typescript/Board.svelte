<script lang="ts">
	import { onDestroy } from 'svelte';
	import { ChessgroundUnstyled as Chessground } from 'svelte-chessground';
	import type { Key } from 'chessground/types';
	import type { Config as ChessgroundConfig } from 'chessground/config';
	import { configuration, chessGame } from './store';
	import { ChessGame } from './chess-game';

	let classes: Array<string> = ['loading'];
	let config: ChessgroundConfig = {};

	const unsubscribeConfiguration = configuration.subscribe(config => {
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

	let game: ChessGame;
	const unsubscribeChessGame = chessGame.subscribe(g => {
		game = g;
	});

	$: if (game) {
		config = game.chessgroundConfig;
	}

	onDestroy(() => {
		unsubscribeConfiguration();
		unsubscribeChessGame();
	});
</script>

<chess-board class={classes.join(' ')}>
	<Chessground {config} />
</chess-board>

<style lang="scss">
	chess-board {
		position: relative;
	}

	chess-board.loading {
		visibility: hidden;
	}
</style>
