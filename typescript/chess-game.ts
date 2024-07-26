import { Chess } from 'chess.js';

type Move = {
	move: string;
	comments: Array<string>;
	nag: number;
}

type Line = {
	fen: string;
	game_comments: Array<string>;
	moves: Array<Move>;
	responses: Array<Move>;
}

export class ChessGame {
	private readonly _chess: Chess;
	private readonly _line: Line;

	constructor() {
		const appElement = document.getElementById('app');
		this._line = JSON.parse(appElement?.dataset.line as string) as Line;

		this._chess = new Chess(this._line.fen);
		for (const move of this._line.moves) {
			this._chess.move(move.move);
			console.log(move.move);
		}
	}

	get chess(): Chess {
		return this._chess;
	}

	get line(): Line {
		return this._line;
	}
}
