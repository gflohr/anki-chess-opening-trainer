import { Chessground } from 'chessground';

type Options = {
	element: HTMLElement;
	prefix: string;
};

export class Page {
	private readonly element: HTMLElement;
	private readonly prefix: string;

	constructor(options: Options) {
		this.element = options.element;
		this.prefix = options.prefix;
	}

	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	render(_: unknown) {
		Chessground(this.element, {
			coordinates: true,
		});
	}
}
