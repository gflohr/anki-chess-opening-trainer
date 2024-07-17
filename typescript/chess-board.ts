import { Chessground } from 'chessground';
import { h, VNode } from 'snabbdom';
import { Config } from './config';

export class ChessBoard {
	render(parent: HTMLElement) {
		const boardElem = parent.querySelector('chess-board');
		if (boardElem) {
			Chessground(boardElem as HTMLElement, {
				coordinates: true,
			});
		}
	}

	node(config: Config): VNode {
		const classes: { [klass: string]: boolean } = {};
		classes['is2d'] = !config.board['3D'];
		classes['is3d'] = config.board['3D'];
		const boardClass2D = ('cot-board-' + config.board['2Dboard']) as string;
		classes[boardClass2D] = true;

		const boardNode = h('chess-board', {
			class: {
				'cg-wrap': true,
				'orientation-white': true,
				manipulable: true,
			},
		});
		return h(
			'chess-wrapper',
			{
				class: classes,
			},
			[boardNode],
		);
	}
}
