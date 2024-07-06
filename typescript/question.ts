import { Chessground } from 'chessground'
import { Page } from "./page.ts";

type Options = {
	element: HTMLElement,
	fen: string,
};

export class Question extends Page {
	constructor(options: Options) {
		super();
		const config = {
			fen: options.fen,
		};
		Chessground(options.element, config);
	}
}
