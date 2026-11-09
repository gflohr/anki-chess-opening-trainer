import type { GameGraph, GraphMove } from './types';

export class GameGraphService {
	constructor(private readonly graph: GameGraph) {}

	findLeaf(): GraphMove | null {
		if (!this.graph.length) {
			return null;
		}

		let node = this.graph[0];
		while (node) {
			if (node[0].next) {
				node = this.graph[node[0].next];
			} else {
				if (node.length > 1) {
					throw new Error('Game graph has more than one leaf!');
				}

				return node[0];
			}
		}

		throw new Error('Could not find leaf in game graph.');
	}
}
