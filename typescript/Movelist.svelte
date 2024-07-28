<script lang="ts">
	import { onDestroy } from 'svelte';
	import { chessTask } from './store';
	import { type Move, BLACK, WHITE } from 'chess.js';
	import { ChessTask } from './chess-task';

	type MovelistMove = {
		moveNumber: number;
		white: string;
		black: string;
	};

	type ChessMove = Move & {
		comment: string;
	};

	let moves: Array<MovelistMove | string> = [];
	let task: ChessTask;

	const unsubscribeChessTask = chessTask.subscribe(t => {
		task = t;
		const chess = task.chess;

		const history = chess.history({ verbose: true }) as Array<ChessMove>;
		const comments = chess.getComments();

		for (const i in history) {
			history[i].comment = comments[i].comment;
		}

		moves = [];
		if (task.gameComments.length) {
			moves.push(task.gameComments);
		}

		let moveNumber = task.firstMoveNumber;
		let move = createMove(moveNumber);

		for (let i = 0; i < history.length; ++i) {
			const entry = history[i];

			if (i === 0 && entry.color === BLACK) {
				move.white = '...';
			}

			if (entry.color === WHITE) {
				move.white = getSAN(entry);
			} else {
				move.black = getSAN(entry);
			}

			if (entry.comment.length) {
				if (entry.color === WHITE) {
					move.black = '...';
					moves.push(move);
					move = createMove(moveNumber);
					move.white = '...';
				} else {
					moves.push(move);
					move = createMove(moveNumber++);
				}

				moves.push(entry.comment);
				continue;
			}

			if (entry.color === BLACK) {
				moves.push(move);
				move = createMove(++moveNumber);
			}
		}

		if (move.white.length) {
			moves.push(move);
		}
	});

	function createMove(moveNumber: number): MovelistMove {
		return {
			moveNumber,
			white: '',
			black: '',
		};
	}

	function getSAN(move: ChessMove): string {
		return move.san;
	}

	onDestroy(() => {
		unsubscribeChessTask();
	});
</script>

<chess-navigation>
	<button>&nbsp;&nbsp;=&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;|&lt;&lt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&lt;&lt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&gt;&gt;&nbsp;&nbsp;</button>
	<button>&nbsp;&nbsp;&gt;&gt;|&nbsp;&nbsp;</button>
</chess-navigation>
<chess-movelist>
	{#each moves as entry}
		{#if typeof entry === 'string'}
			<chess-comment>{entry}</chess-comment>
		{:else}
			<chess-move>
				<chess-move-number>{entry.moveNumber}</chess-move-number>
				<chess-move-white
					class:current-move={task.currentMoveNumber - 1 === entry.moveNumber &&
						task.currentColor === BLACK &&
						entry.white !== '...'}
					class:ellipsis={entry.white === '...'}
				>
					<san>{entry.white}</san>
				</chess-move-white>
				<chess-move-black
					class:current-move={task.currentMoveNumber - 1 === entry.moveNumber &&
						task.currentColor === WHITE &&
						entry.black !== '...'}
					class:ellipsis={entry.black === '...'}
					>
					<san>{entry.black}</san>
				</chess-move-black>
			</chess-move>
		{/if}
	{/each}
	<chess-move>
		<chess-move-number>3</chess-move-number>
		<chess-move-white class="answer-right"><san>Bb5</san></chess-move-white>
		<chess-move-black></chess-move-black>
	</chess-move>
</chess-movelist>

<style lang="scss">
	chess-navigation {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
	}

	chess-navigation button {
		padding: 0.5rem;
		border: none;
	}

	chess-movelist {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
		align-content: start;
		overflow-y: auto;
	}

	chess-move {
		grid-column: span 5;
		font-size: 14pt;
		display: grid;
		grid-template-columns: 1fr 2fr 2fr;
		justify-items: center;
	}

	chess-move-number,
	chess-move-white,
	chess-move-black,
	chess-navigation,
	chess-comment {
		border-bottom: 1px solid #ddd;
	}

	chess-move-number,
	chess-comment {
		background-color: #eee;
	}

	chess-move-number,
	chess-move-white,
	chess-move-black {
		justify-self: center;
		display: flex;
		justify-content: center;
		align-items: center;
		width: 100%;
		height: 100%;
	}

	chess-move-white,
	chess-move-black,
	chess-comment {
		color: #666;
		border-right: 1px solid #ddd;
	}

	chess-move-white:not(.ellipsis):hover,
	chess-move-black:not(.ellipsis):hover {
		color: white;
		background-color: #1b78cf;
		cursor: pointer;
	}

	.current-move {
		background-color: lightblue;
	}

	chess-comment {
		grid-column: span 5;
		font-size: 11pt;
		padding: 4pt;
	}

	.answer-right {
		color: rgb(27, 80, 27);
		font-weight: bold;
	}

	.answer-wrong {
		color: rgb(172, 38, 38);
		font-weight: bold;
	}
</style>
