// frontend/domain/GameSession.svelte.ts
import type { Game } from './types.js';

export class GameSession {
	// Reactive State.
	game = $state<Game>({
		gameAnnotations: { comments: [], markers: [] },
		questionMoves: [],
		answerMoves: [],
		history: [],
	});

	constructor(initialGame: Game) {
		this.game = initialGame;
	}
}
