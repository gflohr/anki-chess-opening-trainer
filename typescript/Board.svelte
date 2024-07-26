<script lang="ts">
	import { onDestroy } from 'svelte';
	import { ChessgroundUnstyled as Chessground } from 'svelte-chessground';
	import { configuration, chessGame } from './store';
	import type { ChessGame } from './chess-game';

	let classes: Array<string> = ['loading'];
	const params = new URLSearchParams(document.location.search);
	const configMode = params.has('configure');

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

	onDestroy(() => {
		unsubscribeConfiguration();
	});
</script>

<chess-board class={classes.join(' ')}>
	<Chessground
		addPieceZIndex={true}
		viewOnly={configMode}
		fen={game.chess.fen()}
	/>
</chess-board>

<style lang="scss">
	chess-board {
		position: relative;
	}

	chess-board.loading {
		visibility: hidden;
	}
</style>
