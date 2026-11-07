// frontend/domain/GameSession.svelte.ts
import type { Game } from './types.js';

export class GameSession {
	// Reactive State
	game = $state<Game>({
		gameAnnotations: { comments: [], markers: [] },
		questionMoves: [],
		answerMoves: [],
		history: [],
	});

	// FIXME! This is redundant.
	isAnswerPhase = $state<boolean>(false);

	// FIXME! This is redundant.
	selectedMoveId = $state<number>(0);

	// Derived State.
	activeDiagramIndex = $derived.by(() => {
		if (!this.isAnswerPhase) return -1; // Question side
		if (!this.selectedMoveId) return 0;

		return this.game.answerMoves.findIndex(
			m => m.id === this.selectedMoveId,
		);
	});

	isInteractive = $derived(!this.isAnswerPhase && !!this.game.initial);

	constructor(initialGame: Game) {
		this.game = initialGame;
	}

	/**
	 * Submit a move attempt during the question phase
	 */
	submitMove(san: string): boolean {
		if (this.isAnswerPhase) return false;

		const move = this.game.answerMoves.find(ans => ans.san === san);
		if (move) {
			move.status = 'correct';
			this.game.history.push(move);

			return true;
		} else {
			this.game.history.push({
				san,
				id: this.nextMoveId(),
				status: 'wrong',
			});

			return false;
		}
	}

	private nextMoveId(): number {
		return (
			1 +
			this.game.questionMoves.length +
			this.game.answerMoves.length +
			this.game.history.length
		);
	}

	/**
	 * Called when transitioning from Question card to Answer card in Anki
	 */
	revealAnswers(): void {
		this.isAnswerPhase = true;

		// Add any missing correct moves that the user did not attempt.
		this.game.history ??= [];
		for (const answer of this.game.answerMoves) {
			const attempted = this.game.history.some(m => m.san === answer.san);
			if (!attempted) {
				this.game.history.push({
					...answer,
					status: 'missing',
				});
			}
		}
	}

	/**
	 * Select a move in the move table
	 */
	selectMove(san: string): void {
		// In legacy SVG mode, restrict clicking to answered/visible positions
		this.selectedMoveSan = san;
	}
}
