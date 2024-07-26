import { writable } from 'svelte/store';
import { type Config } from './config';
import { ChessGame } from './chess-game';

export const configuration = writable<Config | undefined>();
const game = new ChessGame();
export const chessGame = writable(game);
