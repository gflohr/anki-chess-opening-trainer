import * as v from 'valibot';

import { GameSession } from './domain/GameSession.svelte';
import type {
	Game,
	GameNode,
	GraphMove,
	Marker,
	MarkerColour,
	Move,
	Square,
} from './domain/types';

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
const rawConfigSchema = v.object({
	/** SVG images if present. Optional. */
	i: v.optional(
		v.object({
			/** Question diagram. */
			q: v.pipe(v.string(), v.minLength(1)),

			/** Answer diagrams. */
			a: v.array(v.pipe(v.string(), v.minLength(1))),
		}),
	),

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

export type RawConfig = v.InferOutput<typeof rawConfigSchema>;

export interface Config {
	images?: {
		question: string;
		answers: string[];
	};
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

function translateRawMove(raw: RawMove, id: number): Move {
	const move: Move = {
		id,
		san: raw.s,
		annotations: {
			markers: (raw.m ?? []).map(translateRawMarker),
			comments: [...(raw.c ?? [])],
		},
	};

	return move;
}

function translateRawGraphMove(raw: RawGraphMove, id: number): GraphMove {
	const graphMove: GraphMove = translateRawMove(raw, id);
	if (raw.n) graphMove.next = raw.n;

	return graphMove;
}

function translateRawGameNode(raw: RawGameNode, id: number): GameNode {
	const node: GameNode = [];

	for (const graphMove of raw) {
		node.push(translateRawGraphMove(graphMove, id++));
	}

	return node;
}

export function translateRawConfig(input: unknown): Config {
	const result = v.safeParse(rawConfigSchema, input);

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

	let moveId = 0;
	for (const m of raw.s.m ?? []) {
		game.questionMoves.push(translateRawGameNode(m, ++moveId));
		moveId += game.questionMoves[game.questionMoves.length - 1].length - 1;
	}
	for (const a of raw.s.a) {
		game.answerMoves.push(translateRawMove(a, ++moveId));
	}

	const session = new GameSession(game);

	const config: Config = {
		session,
		isQuestion: !!raw.q,
	};

	if (raw.i) {
		config.images = {
			question: raw.i.q,
			answers: [...raw.i.a],
		};
	}

	return config;
}
