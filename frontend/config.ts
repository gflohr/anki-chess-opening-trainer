import { GameSession } from './domain/GameSession.svelte';
import type { Game, Marker, MarkerColour, Move, Square } from './domain/types';

export interface RawMove {
	s: string; /** SAN. */
	m?: string[]; /** Marker annotations in compact form. */
	c?: string[]; /** Comments. */
}

export interface RawConfig {
	/** SVG images if present. */
	i: {
		/** Question diagram. */
		q: string;

		/** Answer diagrams. */
		a: string[]
	},

	/** Game session. */
	s: {
		/** Raw moves. */
		m: RawMove[];

		/** Raw answer moves. */
		a: RawMove[];
	},

	/** Raw game markers. */
	m?: string[];

	/** Game comments. */
	c?: string[];
}

export interface Config {
	images: {
		question: string;
		answers: string[];
	};
	session: GameSession;
}

function translateRawMarker(raw: string): Marker | null {
	if (raw.match(/^[ac][gbyr][a-h][1-8](?:[a-h][1-8])$/)) {
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
			if (raw.length !== 6) {
				return null;
			}

			return {
				type: 'arrow',
				colour,
				from,
				to: `${raw[4]}${raw[5]}` as Square,
			};
		} else {
			if (raw.length !== 4) {
				return null;
			}

			return {
				type: 'circle',
				colour,
				from,
			};
		}
	}

	return null;
}

function translateRawMove(raw: RawMove, id: number): Move {
	const move: Move = {
		id,
		san: raw.s,
	};

	move.annotations = {
		markers: [],
		comments: [...(raw.c ?? [])],
	};

	if (raw.m) {
		for (const rawMarker of raw.m) {
			const marker = translateRawMarker(rawMarker);
			if (marker) {
				move.annotations.markers?.push(marker);
			}
		}
	}

	return move;
}

export function translateRawConfig(raw: RawConfig): Config {
	const markers = (raw.m ?? []).map(m => translateRawMarker(m)).filter(m => m !== null);

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
	for (const m of raw.s.m) {
		game.questionMoves.push(translateRawMove(m, ++moveId));
	}
	for (const a of raw.s.a) {
		game.answerMoves.push(translateRawMove(a, ++moveId));
	}

	const session = new GameSession(game);

	const config: Config = {
		images: {
			question: raw.i.q,
			answers: [...raw.i.a],
		},
		session,
	};

	if (raw.i) {
		config.images = {
			question: raw.i.q,
			answers: raw.i.a,
		};
	}

	return config;
};
