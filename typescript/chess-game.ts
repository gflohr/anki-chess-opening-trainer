import { Chess, type Color, type Square, SQUARES } from 'chess.js';

type LineMove = {
	move: string;
	comments: Array<string>;
	nag: number;
};

type Line = {
	fen: string;
	game_comments: Array<string>;
	moves: Array<LineMove>;
	responses: Array<LineMove>;
};

export class ChessGame {
	private readonly _chess: Chess;
	private readonly _line: Line;
	private readonly _firstMoveNumber: number;
	private _currentMoveNumber: number;
	private _currentColor: Color;

	constructor() {
		const appElement = document.getElementById('app');
		this._line = JSON.parse(appElement?.dataset.line as string) as Line;

		this._chess = new Chess(this._line.fen);
		this._firstMoveNumber = this._chess.moveNumber();
		for (const move of this._line.moves) {
			this._chess.move(move.move);
			this._chess.setComment(move.comments.join('\n'));
		}
		this._currentMoveNumber = this._chess.moveNumber();
		this._currentColor = this._chess.turn();
	}

	toDests(): Map<Square, Array<Square>> {
		const dests = new Map<Square, Array<Square>>();

		SQUARES.forEach(s => {
			const ms = this._chess.moves({square: s, verbose: true});
			if (ms.length) dests.set(s, ms.map(m => m.to));
		});

		return dests;
	}

	get chess(): Chess {
		return this._chess;
	}

	get line(): Line {
		return this._line;
	}

	get firstMoveNumber(): number {
		return this._firstMoveNumber;
	}

	get currentMoveNumber(): number {
		return this._currentMoveNumber;
	}

	get currentColor(): Color {
		return this._currentColor;
	}

	get gameComments(): string {
		return this._line.game_comments.join('\n');
	}
}
