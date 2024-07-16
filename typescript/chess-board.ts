import { Chessground } from 'chessground';
import { h, VNode } from 'snabbdom';

export class ChessBoard {
	render(parent: HTMLElement) {
		const boardElem = parent.querySelector('chess-board');
		if (boardElem) {
			Chessground(boardElem as HTMLElement, {
				coordinates: true,
			});
		}
	}

	node(): VNode {
		const boardNode = h('chess-board', {
			class: {
				'cg-wrap': true,
				'orientation-white': true,
				manipulable: true,
			},
		});
		return h(
			'section',
			{
				class: {
					is2d: true,
					//blue: true,
					//merida: true,
				},
			},
			[boardNode],
		);
	}
}
