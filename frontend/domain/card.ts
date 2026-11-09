import * as v from 'valibot';

import { GameSession } from './GameSession.svelte';
import { gameToPgn } from './game-to-pgn';
import type {
	Game,
	GameNode,
	GraphMove,
	Marker,
	MarkerColour,
	Move,
	Square,
} from './types';

/**
 * Validates individual marker strings:
 * - dtarts with 'a' (length 6) or 'c' (length 4)
 * - decond character is color [g, b, y, r]
 * - followed by 1 square ([a-h][1-8]) for circles or 2 squares for arrows
 */
const rawMarkerSchema = v.pipe(
	v.string(),
	v.regex(/^[ac][gbyr][a-h][1-8](?:[a-h][1-8])?$/, 'Invalid marker format.'),
	v.check((val: string) => {
		if (val[0] === 'a') return val.length === 6;
		if (val[0] === 'c') return val.length === 4;
		return false;
	}, 'Arrow markers (a) must be 6 characters; circle markers (c) must be 4 characters.'),
);

/**
 * Valibot schema for the RawMove interface.
 */
export const rawMoveSchema = v.object({
	/** SAN of the move. */
	s: v.string(),

	/** Index of the move. */
	i: v.pipe(v.number(), v.minValue(1)),

	/** Optional marker annotations. */
	m: v.optional(v.array(rawMarkerSchema)),

	/** Optional comments. */
	c: v.optional(v.array(v.string())),
});

type RawMove = v.InferOutput<typeof rawMoveSchema>;

/**
 * Valibot schema for raw graph moves (extends rawMoveSchema with optional target node index).
 */
export const rawGraphMoveSchema = v.object({
	...rawMoveSchema.entries,
	/** Target node index. Optional: defaults to next sequential node if omitted. */
	n: v.optional(v.pipe(v.number(), v.minValue(1))),
});

export type RawGraphMove = v.InferOutput<typeof rawGraphMoveSchema>;

/** One node in a game. Its moves lead to other nodes. */
export const rawGameNodeSchema = v.array(rawGraphMoveSchema);

export type RawGameNode = v.InferOutput<typeof rawGameNodeSchema>;

/** A complete game graph. */
export const rawGameGraphSchema = v.array(rawGameNodeSchema);

export type RawGameGraph = v.InferOutput<typeof rawGameGraphSchema>;

/**
 * Validates raw configuration as passed on the card body.
 */
const rawCardSchema = v.object({
	// FIXME! The properties f and i must be mutually exclusive!
	/** Initial FEN. */
	f: v.optional(v.pipe(v.string(), v.minLength(20))),

	/** SVG images if present. Optional. */
	i: v.optional(v.array(v.pipe(v.string()))),

	/** Game session. */
	s: v.object({
		/** Raw (question) moves (optional prefix question moves). */
		m: v.optional(rawGameGraphSchema),

		/** Raw answer moves. */
		a: v.pipe(v.array(rawMoveSchema), v.minLength(1)),
	}),

	/** Raw game markers. */
	m: v.optional(v.array(rawMarkerSchema)),

	/** Game comments. */
	c: v.optional(v.array(v.string())),

	/** True for questions. */
	q: v.optional(v.boolean()),
});

export type RawCard = v.InferOutput<typeof rawCardSchema>;

export interface Card {
	fen?: string;
	images?: string[];
	session: GameSession;
	isQuestion: boolean;
}

function translateRawMarker(raw: string): Marker {
	const from = `${raw[2]}${raw[3]}` as Square;

	let colour: MarkerColour;
	switch (raw[1]) {
		case 'b':
			colour = 'blue';
			break;
		case 'y':
			colour = 'yellow';
			break;
		case 'r':
			colour = 'red';
			break;
		default:
			colour = 'green';
			break;
	}

	if (raw[0] === 'a') {
		return {
			type: 'arrow',
			colour,
			from,
			to: `${raw[4]}${raw[5]}` as Square,
		};
	} else {
		return {
			type: 'circle',
			colour,
			from,
		};
	}
}

function translateRawMove(raw: RawMove): Move {
	const move: Move = {
		id: raw.i,
		san: raw.s,
		annotations: {
			markers: (raw.m ?? []).map(translateRawMarker),
			comments: [...(raw.c ?? [])],
		},
	};

	return move;
}

function translateRawGraphMove(raw: RawGraphMove): GraphMove {
	const graphMove: GraphMove = translateRawMove(raw);
	if (raw.n) graphMove.next = raw.n;

	return graphMove;
}

function translateRawGameNode(raw: RawGameNode): GameNode {
	const node: GameNode = [];

	for (const graphMove of raw) {
		node.push(translateRawGraphMove(graphMove));
	}

	return node;
}

export function translateRawCard(input: unknown): Card {
	const result = v.safeParse(rawCardSchema, input);

	if (!result.success) {
		const errorMessage = result.issues
			.map(issue => {
				const path = issue.path
					? issue.path.map(p => p.key).join('.')
					: '';

				const message = `${issue.message} ('${issue.input}');`;
				return path ? `${path}: ${message}` : message;
			})
			.join('; ');
		throw new Error(`Invalid card configuration: ${errorMessage}`);
	}

	const raw = result.output;

	const markers = (raw.m ?? []).map(translateRawMarker);

	const game = {
		gameAnnotations: {
			comments: [...(raw.c ?? [])],
			markers,
		},
		questionMoves: [],
		answerMoves: [],
		history: [],
	} as Game;

	for (const m of raw.s.m ?? []) {
		game.questionMoves.push(translateRawGameNode(m));
	}
	for (const a of raw.s.a) {
		game.answerMoves.push(translateRawMove(a));
	}

	const session = new GameSession(game);

	const card: Card = {
		session,
		isQuestion: !!raw.q,
	};

	if (raw.f) {
		card.fen = raw.f;
	}

	if (raw.i) {
		card.images = [...raw.i];
	}

	try {
		game.pgn = gameToPgn(game);
	} catch (e) {
		console.error('Error generating PGN from game graph:', e);
	}

	return card;
}
