import { writable } from 'svelte/store';
import { type Config as ChessgroundConfig } from 'chessground/config';
import { type Config } from './config';
import { ChessGame } from './chess-game';

export const configuration = writable<Config | undefined>();

const params = new URLSearchParams(document.location.search);
const configMode = params.has('configure');
const chessgroundConfig: ChessgroundConfig = {
	addPieceZIndex: true,
	viewOnly: configMode,
}

const game = new ChessGame(chessgroundConfig);
export const chessGame = writable(game);
