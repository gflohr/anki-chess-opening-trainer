import { describe, expect, it } from 'vitest';
import { type RawConfig, translateRawConfig } from './config';

describe('translateRawConfig', () => {
	it('successfully parses a valid complete configuration', () => {
		const input: RawConfig = {
			i: {
				q: 'data:image/svg+xml;base64,question',
				a: ['data:image/svg+xml;base64,answer1'],
			},
			s: {
				m: [[{ s: 'e4', c: ['King pawn opening'] }]],
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

		// Verify game session data translation.
		const game = config.session.game;
		expect(game.gameAnnotations.comments).toEqual(['Opening overview']);
		expect(game.gameAnnotations.markers).toHaveLength(1);
		expect(game.gameAnnotations.markers[0]).toEqual({
			type: 'circle',
			colour: 'blue',
			from: 'd4',
		});

		expect(game.questionMoves).toHaveLength(1);
		expect(game.questionMoves[0][0].san).toBe('e4');
		expect(game.questionMoves[0][0].annotations!.comments).toEqual([
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

	describe('Game graphs', () => {
		it('should transform a game graph', async () => {
			const input: RawConfig = {
				i: {
					q: 'question.svg',
					a: ['answer1.svg', 'answer2.svg'],
				},
				s: {
					// This game graph represents these opening transpositions:
					//
					// 1. d4 d5 2. c4 e6 3. Nf3  -\
					//                             -> Nc3
					// 1. Nf3 Nf6 2. c4 e6 3. d5 -/
					m: [
						[
							{
								s: 'd4',
								c: ['Queen pawn opening'],
								n: 1,
							},
							{
								s: 'Nf3',
								c: ['Zukertort opening'],
								n: 5,
							},
						],
						[
							{
								s: 'Nf6',
								n: 2,
							},
						],
						[
							{
								s: 'Nf3',
								n: 3,
							},
						],
						[
							{
								s: 'd5',
								n: 4,
							},
						],
						[
							{
								s: 'Nc3',
							},
						],
						[
							{
								s: 'Nf6',
								n: 6,
							},
						],
						[
							{
								s: 'c4',
								n: 7,
							},
						],
						[
							{
								s: 'd4',
								n: 8,
							},
						],
						[
							{
								s: 'd5',
								n: 4,
							},
						],
					],
					a: [{ s: 'Nf6' }, { s: 'g3' }],
				},
			};

			const config = translateRawConfig(input);
			const game = config.session.game;

			expect(game.questionMoves.length).toBe(input.s.m!.length);

			const nodes = game.questionMoves;
			expect(nodes.length).toBe(9);

			expect(nodes[0].length).toBe(2);
			expect(nodes[0][0].next).toBe(1);
			expect(nodes[0][1].next).toBe(5);
			expect(nodes[0][0].id).toBe(1);
			expect(nodes[0][1].id).toBe(2);

			expect(nodes[1].length).toBe(1);
			expect(nodes[1][0].next).toBe(2);
			expect(nodes[1][0].id).toBe(3);

			expect(nodes[2].length).toBe(1);
			expect(nodes[2][0].next).toBe(3);
			expect(nodes[2][0].id).toBe(4);

			expect(nodes[3].length).toBe(1);
			expect(nodes[3][0].next).toBe(4);
			expect(nodes[3][0].id).toBe(5);

			expect(nodes[4].length).toBe(1);
			expect(nodes[4][0].next).not.toBeDefined();
			expect(nodes[4][0].id).toBe(6);

			expect(nodes[5].length).toBe(1);
			expect(nodes[5][0].next).toBe(6);
			expect(nodes[5][0].id).toBe(7);

			expect(nodes[6].length).toBe(1);
			expect(nodes[6][0].next).toBe(7);
			expect(nodes[6][0].id).toBe(8);

			expect(nodes[7].length).toBe(1);
			expect(nodes[7][0].next).toBe(8);
			expect(nodes[7][0].id).toBe(9);

			expect(nodes[8].length).toBe(1);
			expect(nodes[8][0].next).toBe(4);
			expect(nodes[8][0].id).toBe(10);

			await expect(game).toMatchFileSnapshot('__snapshots__/graph.snap');
		});
	});
});
