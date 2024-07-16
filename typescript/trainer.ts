import { init, attributesModule, h, VNode } from 'snabbdom';
import { Config, Meta } from './config';
import { Page } from './page';

type Options = {
	element: HTMLElement;
	prefix: string;
};

const defaultConfig: Config = {};

export class Trainer {
	private readonly prefix: string;
	private readonly page: Page;
	private config: Config = defaultConfig;
	private patch: (
		oldVnode: VNode | Element | DocumentFragment,
		vnode: VNode,
	) => VNode;

	constructor(options: Options) {
		this.prefix = options.prefix;
		this.patch = init([attributesModule]);
		this.insertStylesheets();
		this.page = new Page(options.element);
	}

	async render(line: unknown) {
		const path = `${this.prefix}/meta.json`;

		try {
			const response = await fetch(path);
			const meta: Meta = (await response.json()) as Meta;
			this.config = meta.config;
		} catch (_) {
			/* empty */
		}

		this.page.render(line);
	}

	private insertStylesheets() {
		const bundle = `${this.prefix}/assets/bundle.min.css`;
		const bundleNode = h('link', {
			attrs: { rel: 'stylesheet', href: bundle },
		});
		const pieces = `${this.prefix}/assets/css/pieces/cburnett.css`;
		const piecesNode = h('link', {
			attrs: { rel: 'stylesheet', href: pieces },
		});

		const headNode = h('head', {}, [bundleNode, piecesNode]);

		const headElement = document.getElementsByTagName('head');
		this.patch(headElement[0], headNode);
	}
}
