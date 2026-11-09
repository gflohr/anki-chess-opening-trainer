import { describe, expect, it } from 'vitest';
import { GameGraphService } from './game-graph-service';
import type { GameGraph } from './types';

describe('Game graph service', () => {
	describe('findLeaf()', () => {
		it('should find a leave', () => {
			// Base line: 1. d4 d5 2. Bf4 Nf6 3. Nf3 e6 4. e3 Bd6
			// Encode all transpositions between 1. d4 and 4. e3.
			const graph: GameGraph = [
				[{ san: 'd4', id: 1, next: 1 }],
				[
					{ san: 'd5', id: 2, next: 2 },
					{ san: 'Nf6', id: 3, next: 9 },
					{ san: 'e6', id: 4, next: 13 },
				],
				[
					{ san: 'Bf4', id: 5, next: 3 },
					{ san: 'Nf3', id: 6, next: 15 },
				],
				[
					{ san: 'Nf6', id: 7, next: 4 },
					{ san: 'e6', id: 8, next: 7 },
				],
				[{ san: 'Nf3', id: 9, next: 5 }],
				[{ san: 'e6', id: 10, next: 6 }],
				[{ san: 'e3', id: 11 }],
				[{ san: 'Nf3', id: 12, next: 8 }],
				[{ san: 'Nf6', id: 13, next: 6 }],
				[
					{ san: 'Bf4', id: 14, next: 10 },
					{ san: 'Nf3', id: 15, next: 18 },
				],
				[
					{ san: 'd5', id: 16, next: 4 },
					{ san: 'e6', id: 17, next: 11 },
				],
				[{ san: 'Nf3', id: 18, next: 12 }],
				[{ san: 'd5', id: 19, next: 6 }],
				[
					{ san: 'Bf4', id: 20, next: 14 },
					{ san: 'Nf3', id: 21, next: 20 },
				],
				[
					{ san: 'd5', id: 22, next: 7 },
					{ san: 'Nf6', id: 23, next: 11 },
				],
				[
					{ san: 'Nf6', id: 24, next: 16 },
					{ san: 'e6', id: 25, next: 17 },
				],
				[{ san: 'Bf4', id: 26, next: 5 }],
				[{ san: 'Bf4', id: 27, next: 8 }],
				[
					{ san: 'd5', id: 28, next: 16 },
					{ san: 'e6', id: 29, next: 19 },
				],
				[{ san: 'Bf4', id: 30, next: 12 }],
				[
					{ san: 'd5', id: 31, next: 17 },
					{ san: 'Nf6', id: 32, next: 19 },
				],
			];

			const service = new GameGraphService(graph);
			expect(service.findLeaf()).toStrictEqual({ san: 'e3', id: 11 });
		});

		it('should throw an exception for empty game graphs', () => {
			const service = new GameGraphService([]);
			expect(() => service.findLeaf()).toThrow('Game graph is empty!');
		});

		it('should throw an exception for game graphs with multiple leaves', () => {
			const graph = [
				[{ san: 'd4', id: 1, next: 1}],
				[{ san: 'd5', id: 2, next: 2}],
				[{ san: 'Bf4', id: 3}, { san: 'c4', id: 4 }],
			];
			const service = new GameGraphService(graph);
			expect(() => service.findLeaf()).toThrow('Game graph has more than one leaf!');
		});
	});
});
