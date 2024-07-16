import { Chessground } from 'chessground';

export class Page {
	private readonly parent: HTMLElement;

	constructor(parent: HTMLElement) {
		this.parent = parent;
	}

	// eslint-disable-next-line @typescript-eslint/no-unused-vars
	render(_: unknown) {
		Chessground(this.parent, {
			coordinates: true,
		});
	}
}
