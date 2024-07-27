<script lang="ts">
	import { onDestroy } from 'svelte';
	import { ChessgroundUnstyled as Chessground } from 'svelte-chessground';
	import type { Key } from 'chessground/types';
	import type { Config as ChessgroundConfig } from 'chessground/config';
	import { configuration, chessGame } from './store';
	import { ChessGame } from './chess-game';

	let classes: Array<string> = ['loading'];
	const params = new URLSearchParams(document.location.search);
	const configMode = params.has('configure');
	let viewOnly = configMode;
	let config: ChessgroundConfig = {
		movable: {
			free: false,
		}
	};

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
	const lastMove: Array<Key> = [];
	const unsubscribeChessGame = chessGame.subscribe(g => {
		game = g;

		const history = game.chess.history({ verbose: true });
		if (history.length) {
			const lastEntry = history[history.length - 1];
			lastMove[0] = lastEntry.from
			lastMove[1] = lastEntry.to;
		}

	});

	onDestroy(() => {
		unsubscribeConfiguration();
		unsubscribeChessGame();
	});
</script>

<chess-board class={classes.join(' ')}>
	<Chessground
		addPieceZIndex={true}
		viewOnly={viewOnly}
		fen={game.chess.fen()}
		lastMove={lastMove}
		{config}
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
