export type MarkerColour = 'red' | 'green' | 'blue' | 'yellow';

export type Square =
	| 'a1'
	| 'a2'
	| 'a3'
	| 'a4'
	| 'a5'
	| 'a6'
	| 'a7'
	| 'a8'
	| 'b1'
	| 'b2'
	| 'b3'
	| 'b4'
	| 'b5'
	| 'b6'
	| 'b7'
	| 'b8'
	| 'c1'
	| 'c2'
	| 'c3'
	| 'c4'
	| 'c5'
	| 'c6'
	| 'c7'
	| 'c8'
	| 'd1'
	| 'd2'
	| 'd3'
	| 'd4'
	| 'd5'
	| 'd6'
	| 'd7'
	| 'd8'
	| 'e1'
	| 'e2'
	| 'e3'
	| 'e4'
	| 'e5'
	| 'e6'
	| 'e7'
	| 'e8'
	| 'f1'
	| 'f2'
	| 'f3'
	| 'f4'
	| 'f5'
	| 'f6'
	| 'f7'
	| 'f8'
	| 'g1'
	| 'g2'
	| 'g3'
	| 'g4'
	| 'g5'
	| 'g6'
	| 'g7'
	| 'g8'
	| 'h1'
	| 'h2'
	| 'h3'
	| 'h4'
	| 'h5'
	| 'h6'
	| 'h7'
	| 'h8';

export interface MarkerBase {
	colour: MarkerColour;
	from: Square;
}
export interface Circle extends MarkerBase {
	type: 'circle';
}

export interface Arrow extends MarkerBase {
	type: 'arrow';
	to: Square;
}

export type Marker = Circle | Arrow;

export interface MoveAnnotation {
	comments: string[];
	markers: Marker[];
}

export interface Move {
	/** 1-based index. Index 0 is the initial position. */
	id: number;
	san: string;
	annotations?: MoveAnnotation;
	status?: 'correct' | 'wrong' | 'missing' | 'neutral';
}

/**
 * A move inside a game graph that has successors.
 */
export interface GraphMove extends Move {
	/** The index of the node reached from here. */
	next?: number;
}

/**
 * A node (or leaf) in a game graph.
 */
export type GameNode = GraphMove[];

export type GameGraph = GameNode[];

export interface Game {
	/**
	 * The initial FEN if known.
	 */
	initial?: string;

	gameAnnotations: MoveAnnotation;
	questionMoves: GameGraph;
	answerMoves: Move[];
	history: Move[];
}
