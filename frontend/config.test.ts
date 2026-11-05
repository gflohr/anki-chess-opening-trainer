import { describe, expect, it } from 'vitest';
import { translateRawConfig } from './config';

describe('translateRawConfig', () => {
	it('successfully parses a valid complete configuration', () => {
		const input = {
			i: {
				q: 'data:image/svg+xml;base64,question',
				a: ['data:image/svg+xml;base64,answer1'],
			},
			s: {
				m: [{ s: 'e4', c: ['King pawn opening'] }],
				a: [{ s: 'e5', m: ['cge4', 'arg1f3'] }],
			},
			m: ['cbd4'],
			c: ['Opening overview'],
		};

		const config = translateRawConfig(input);

		expect(config.images).toEqual({
			question: 'data:image/svg+xml;base64,question',
			answers: ['data:image/svg+xml;base64,answer1'],
		});

		// Verify game session data translation
		const game = config.session.game;
		expect(game.gameAnnotations.comments).toEqual(['Opening overview']);
		expect(game.gameAnnotations.markers).toHaveLength(1);
		expect(game.gameAnnotations.markers[0]).toEqual({
			type: 'circle',
			colour: 'blue',
			from: 'd4',
		});

		expect(game.questionMoves).toHaveLength(1);
		expect(game.questionMoves[0].san).toBe('e4');
		expect(game.questionMoves[0].annotations!.comments).toEqual([
			'King pawn opening',
		]);

		expect(game.answerMoves).toHaveLength(1);
		expect(game.answerMoves[0].san).toBe('e5');
		expect(game.answerMoves[0].annotations!.markers).toHaveLength(2);
		// Circle test.
		expect(game.answerMoves[0].annotations!.markers[0]).toEqual({
			type: 'circle',
			colour: 'green',
			from: 'e4',
		});
		// Arrow test.
		expect(game.answerMoves[0].annotations!.markers[1]).toEqual({
			type: 'arrow',
			colour: 'red',
			from: 'g1',
			to: 'f3',
		});
	});

	it('allows optional image block and optional question prefix moves', () => {
		const input = {
			s: {
				a: [{ s: 'Nf3' }],
			},
		};

		const config = translateRawConfig(input);

		expect(config.images).toBeUndefined();
		expect(config.session.game.questionMoves).toHaveLength(0);
		expect(config.session.game.answerMoves).toHaveLength(1);
		expect(config.session.game.answerMoves[0].san).toBe('Nf3');
	});

	it('throws a human-readable validation error for invalid marker format', () => {
		const input = {
			s: {
				a: [{ s: 'e5', m: ['invalid_marker'] }],
			},
		};

		expect(() => translateRawConfig(input)).toThrowError(
			/Invalid card configuration.*Invalid marker format/i,
		);
	});

	it('throws a validation error when required answer moves array is missing', () => {
		const input = {
			s: {
				m: [{ s: 'e4' }],
				// missing 'a'
			},
		};

		expect(() => translateRawConfig(input)).toThrowError(
			/Invalid card configuration/i,
		);
	});
});
