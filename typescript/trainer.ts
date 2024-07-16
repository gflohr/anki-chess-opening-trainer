import { Config, Meta } from "./config";
import { Page } from "./page";

type Options = {
	element: HTMLElement;
	prefix: string;
};

const defaultConfig: Config = {}

export class Trainer {
	private readonly prefix: string;
	private readonly page: Page;
	private config: Config = defaultConfig;

	constructor(options: Options) {
		this.prefix = options.prefix;
		this.page = new Page({ element: options.element, prefix: options.prefix });
		this.insertStylesheets();
	}

	async render(line: unknown) {
		const path = `${this.prefix}/meta.json`;

		try {
			const response = await fetch(path);
			const meta: Meta = await response.json() as Meta;
			this.config = meta.config;
		} catch(_) { /* empty */ }

		this.page.render(line);
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
