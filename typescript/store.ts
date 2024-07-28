import { writable } from 'svelte/store';
import { type Config as ChessgroundConfig } from 'chessground/config';
import { type Config } from './config';
import { ChessTask } from './chess-task';

export const configuration = writable<Config | undefined>();

const params = new URLSearchParams(document.location.search);
const configMode = params.has('configure');
const chessgroundConfig: ChessgroundConfig = {
	addPieceZIndex: true,
	viewOnly: configMode,
}

const task = new ChessTask(chessgroundConfig);
export const chessTask = writable(task);
