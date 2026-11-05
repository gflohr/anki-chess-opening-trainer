import * as v from 'valibot';

import { GameSession } from './domain/GameSession.svelte';
import type { Game, Marker, MarkerColour, Move, Square } from './domain/types';

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
		/** Raw moves (optional prefix question moves). */
		m: v.optional(v.array(rawMoveSchema), []),

		/** Raw answer moves. */
		a: v.pipe(v.array(rawMoveSchema), v.minLength(1)),
	}),

	/** Raw game markers. */
	m: v.optional(v.array(rawMarkerSchema)),

	/** Game comments. */
	c: v.optional(v.array(v.string())),
});

export type RawConfig = v.InferOutput<typeof rawConfigSchema>;

export interface Config {
	images?: {
		question: string;
		answers: string[];
	};
	session: GameSession;
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

export function translateRawConfig(input: unknown): Config {
	const result = v.safeParse(rawConfigSchema, input);

	if (!result.success) {
		const errorMessage = result.issues
			.map(issue => {
				const path = issue.path
					? issue.path.map(p => p.key).join('.')
					: '';

				const message = `${issue.message} ('${issue.input}');`
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
		game.questionMoves.push(translateRawMove(m, ++moveId));
	}
	for (const a of raw.s.a) {
		game.answerMoves.push(translateRawMove(a, ++moveId));
	}

	const session = new GameSession(game);

	const config: Config = {
		session,
	};

	if (raw.i) {
		config.images = {
			question: raw.i.q,
			answers: [...raw.i.a],
		};
	}

	return config;
}
