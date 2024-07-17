import { init, attributesModule, classModule, h, VNode } from 'snabbdom';
import { Config } from './config';
import { defaultConfig } from './default-config';
import { ChessBoard } from './chess-board';

type Options = {
	prefix: string;
	id: string;
};

export type AnkiMeta = {
	config: Config;
};

export class Trainer {
	private readonly prefix: string;
	private config: Config = defaultConfig;
	private patch: (
		oldVnode: VNode | Element | DocumentFragment,
		vnode: VNode,
	) => VNode;
	private readonly id: string;

	constructor(options: Options) {
		this.prefix = options.prefix;
		this.patch = init([attributesModule, classModule]);
		this.id = options.id;
	}

	async render() {
		const path = `${this.prefix}/meta.json`;

		try {
			const response = await fetch(path);
			const meta: AnkiMeta = (await response.json()) as AnkiMeta;
			this.config = meta.config;
		} catch (_) {
			/* empty */
		}

		this.insertStylesheets();

		const board = new ChessBoard();
		const boardNode = board.node();
		const sidebarNode = h('chess-sidebar');
		const containerNode = h(
			'chess-opening-trainer',
			{
				attrs: {
					id: this.id,
				},
			},
			[boardNode, sidebarNode],
		);

		const bodyNode = h('body', {}, [containerNode]);

		const bodyElement = document.querySelector('body') as HTMLElement;
		this.patch(bodyElement, bodyNode);

		const container = document.getElementById(this.id);
		if (container) {
			board.render(container);
		}
	}

	private insertStylesheets() {
		const bundle = `${this.prefix}/assets/bundle.min.css`;
		const bundleNode = h('link', {
			attrs: { rel: 'stylesheet', href: bundle },
		});
		const pieces2D = this.config.board['2Dpieces'];
		const pieces = `${this.prefix}/assets/css/pieces/${pieces2D}.css`;
		const piecesNode = h('link', {
			attrs: { rel: 'stylesheet', href: pieces },
		});

		const headNode = h('head', {}, [bundleNode, piecesNode]);

		const headElement = document.querySelector('head') as HTMLElement;
		this.patch(headElement, headNode);
	}
}
