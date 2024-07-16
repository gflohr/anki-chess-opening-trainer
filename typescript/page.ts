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
		this.insertStylesheets();
	}

	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	render(_: unknown) {
		Chessground(this.element, {
			coordinates: true,
		});
	}

	private insertStylesheets() {
		const head = document.getElementsByTagName('head')[0];

		const bundleStylesheet = document.createElement('link');
		bundleStylesheet.setAttribute('rel', 'stylesheet');
		bundleStylesheet.setAttribute('href', `${this.prefix}/assets/bundle.min.css`);
		head.appendChild(bundleStylesheet);

		const piecesStylesheet = document.createElement('link');
		piecesStylesheet.setAttribute('id', 'chess-opening-trainer-pieces-styles');
		piecesStylesheet.setAttribute('rel', 'stylesheet');
		piecesStylesheet.setAttribute('href', `${this.prefix}/assets/css/pieces/cburnett.css`);
		head.appendChild(piecesStylesheet);
	}
}
