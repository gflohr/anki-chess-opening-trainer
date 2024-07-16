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
		this.page = new Page({ element: options.element, prefix: options.prefix })
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
}
