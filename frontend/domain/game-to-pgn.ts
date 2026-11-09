import { Chess } from 'chess.js';
import type {
	Game,
	GameGraph,
	GameNode,
	GraphMove,
	Marker,
	Move,
	MoveAnnotation,
} from './types.js';

function getMarkerColorPrefix(color: string): string {
	switch (color) {
		case 'red':
			return 'R';
		case 'green':
			return 'G';
		case 'blue':
			return 'B';
		case 'yellow':
			return 'Y';
		default:
			return 'G';
	}
}

function formatMarkersPGN(markers: Marker[] = []): string {
	if (!markers || markers.length === 0) return '';

	const circles: string[] = [];
	const arrows: string[] = [];

	for (const m of markers) {
		const colorCode = getMarkerColorPrefix(m.colour);
		if (m.type === 'circle') {
			circles.push(`${colorCode}${m.from}`);
		} else if (m.type === 'arrow') {
			arrows.push(`${colorCode}${m.from}${m.to}`);
		}
	}

	const parts: string[] = [];
	if (circles.length > 0) parts.push(`[%csl ${circles.join(',')}]`);
	if (arrows.length > 0) parts.push(`[%cal ${arrows.join(',')}]`);

	return parts.join(' ');
}

function formatAnnotation(annotation?: MoveAnnotation): string {
	if (!annotation) return '';

	const commentsText = annotation.comments?.join(' ').trim() ?? '';
	const markersText = formatMarkersPGN(annotation.markers);

	const fullComment = [commentsText, markersText]
		.filter(Boolean)
		.join(' ')
		.trim();
	return fullComment ? ` { ${fullComment} }` : '';
}

/**
 * Recursively serializes a graph node and its children, formatting alternative
 * moves at the same node as inline PGN variations.
 */
function serializeNode(
	graph: GameGraph,
	nodeIndex: number,
	chess: Chess,
	isContinuation = false,
): string {
	if (!graph || graph.length === 0 || !graph[nodeIndex]) return '';

	const node: GameNode = graph[nodeIndex];
	if (!node || node.length === 0) return '';

	const [primaryMove, ...altMoves] = node;
	let result = '';

	const moveNumber = chess.moveNumber();
	const isWhite = chess.turn() === 'w';

	if (isWhite) {
		result += `${moveNumber}. `;
	} else if (!isContinuation) {
		result += `${moveNumber}... `;
	}

	result += `${primaryMove.san}${formatAnnotation(primaryMove.annotations)}`;

	// 1. Serialize inline variations IMMEDIATELY after primary move
	for (const altMove of altMoves) {
		const altChess = new Chess(chess.fen());
		const altMoveNumber = altChess.moveNumber();
		const altIsWhite = altChess.turn() === 'w';

		const altPrefix = altIsWhite
			? `${altMoveNumber}. `
			: `${altMoveNumber}... `;
		let altSubStr = `${altPrefix}${altMove.san}${formatAnnotation(altMove.annotations)}`;

		if (altMove.next !== undefined && graph[altMove.next]) {
			doMove(altChess, altMove);
			const subNext = serializeNode(graph, altMove.next, altChess, true);
			if (subNext) altSubStr += ` ${subNext}`;
		}

		result += ` (${altSubStr})`;
	}

	// 2. Advance main line and serialize child nodes
	const primaryChess = new Chess(chess.fen());
	doMove(primaryChess, primaryMove);

	if (primaryMove.next !== undefined && graph[primaryMove.next]) {
		// If altMoves were printed, the next main line move needs a move number re-established
		const nextIsContinuation = altMoves.length === 0 ? true : false;
		const subNext = serializeNode(
			graph,
			primaryMove.next,
			primaryChess,
			nextIsContinuation,
		);
		if (subNext) result += ` ${subNext}`;
	}

	return result;
}

function doMove(chess: Chess, move: Move) {
	try {
		chess.move(move.san);
	} catch (e) {
		throw new Error(
			`Applying move id '${move.id}' failed from position '${chess.fen()}': ${e}`,
		);
	}
}

export function gameToPgn(game: Game): string {
	const headers: string[] = [];

	const initialFen =
		game.initial ||
		'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
	const chess = new Chess(initialFen);

	if (
		game.initial &&
		game.initial !==
			'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
	) {
		headers.push(`[SetUp "1"]`);
		headers.push(`[FEN "${game.initial}"]`);
	}

	const pgnText = headers.length ? headers.join('\n') + '\n\n' : '';
	let pgnBody = '';

	if (game.questionMoves && game.questionMoves.length > 0) {
		pgnBody += serializeNode(game.questionMoves, 0, chess);

		let currNodeIdx: number | undefined = 0;
		while (
			currNodeIdx !== undefined &&
			game.questionMoves[currNodeIdx]?.[0]
		) {
			const m: GraphMove = game.questionMoves[currNodeIdx][0];
			doMove(chess, m);
			currNodeIdx = m.next;
		}
	}

	const [mainAnswer, ...variations] = game.answerMoves;
	const moveNumber = chess.moveNumber();
	const isWhite = chess.turn() === 'w';
	const movePrefix = isWhite ? `${moveNumber}. ` : '';

	pgnBody += ` ${movePrefix}${mainAnswer.san}${formatAnnotation(mainAnswer.annotations)}`;

	for (const altMove of variations) {
		pgnBody += ` (${movePrefix}${altMove.san}${formatAnnotation(altMove.annotations)})`;
	}

	pgnBody += ' *';
	return (pgnText + pgnBody.trim()).trim();
}
