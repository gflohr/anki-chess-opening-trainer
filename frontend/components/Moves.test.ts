import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import Moves from '../components/Moves.svelte';
import type { Card } from '../domain/card.js';

describe('Moves Component', () => {
	describe('Question Side', () => {
		const mockCard: Partial<Card> = {
			isQuestion: true,
			session: {
				game: {
					gameAnnotations: { comments: [], markers: [] },
					questionMoves: [
						[{ id: 1, san: 'e4', next: 1 }],
						[{ id: 2, san: 'e5' }],
					],
					answerMoves: [
						{ id: 3, san: 'Nf3' },
						{ id: 4, san: 'Bc4' },
					],
					history: [],
				},
			},
			images: {
				question: 'question.png',
				answers: [],
			},
		} as unknown as Partial<Card>;

		it('renders question moves correctly and hides answers', () => {
			render(Moves, { pcard: mockCard });

			expect(screen.queryByText('e4')).not.toBeNull();
			expect(screen.queryByText('e5')).not.toBeNull();
			expect(screen.queryByText('Nf3')).toBeNull();
			expect(screen.queryByText('Bc4')).toBeNull();
		});

		it('sets the final leaf as active and non-clickable by default on the question side', () => {
			render(Moves, { pcard: mockCard });

			const e4Cell = screen.getByText('e4').closest('td');
			const e5Cell = screen.getByText('e5').closest('td');

			// Non-leaf (e4) should be clickable (since it's not active)
			expect(e4Cell?.classList.contains('clickable')).toBe(false);
			expect(e4Cell?.classList.contains('active-move')).toBe(false);

			// Final leaf (e5) should be active and NOT clickable
			expect(e5Cell?.classList.contains('clickable')).toBe(false);
			expect(e5Cell?.classList.contains('active-move')).toBe(true);
		});
	});

	describe('Answer Side', () => {
		const mockCard: Partial<Card> = {
			session: {
				game: {
					gameAnnotations: { comments: [], markers: [] },
					questionMoves: [
						[{ id: 1, san: 'e4', next: 1 }],
						[{ id: 2, san: 'e5' }],
					],
					answerMoves: [
						{ id: 3, san: 'Nf3' },
						{ id: 4, san: 'Bc4' },
					],
					history: [],
				},
			},
			images: {
				question: 'question.png',
				answers: [],
			},
		} as unknown as Partial<Card>;

		it('renders question and answer moves correctly', () => {
			render(Moves, { pcard: mockCard });

			expect(screen.queryByText('e4')).not.toBeNull();
			expect(screen.queryByText('e5')).not.toBeNull();
			expect(screen.queryByText('Nf3')).not.toBeNull();
			expect(screen.queryByText('Bc4')).not.toBeNull();
		});

		it('sets the first answer as active and non-clickable by default on the answer side', () => {
			render(Moves, { pcard: mockCard });

			const e4Cell = screen.getByText('e4').closest('td');
			const e5Cell = screen.getByText('e5').closest('td');
			const nf3Cell = screen.getByText('Nf3').closest('td');
			const bc4Cell = screen.getByText('Bc4').closest('td');

			// History move (e4) should be clickable (since it's not active).
			expect(e4Cell?.classList.contains('clickable')).toBe(false);
			expect(e4Cell?.classList.contains('active-move')).toBe(false);

			// Final question move (e5) should not be active but clickable.
			expect(e5Cell?.classList.contains('clickable')).toBe(true);
			expect(e5Cell?.classList.contains('active-move')).toBe(false);

			// First answer move (Nf3) should be active but not clickable.
			expect(nf3Cell?.classList.contains('clickable')).toBe(false);
			expect(nf3Cell?.classList.contains('active-move')).toBe(true);

			// Second answer move (Bc4) should not be active but clickable.
			expect(bc4Cell?.classList.contains('clickable')).toBe(true);
			expect(bc4Cell?.classList.contains('active-move')).toBe(false);
		});

		it('allows clicking the question move', async () => {
			render(Moves, { pcard: mockCard });

			const e5Cell = screen.getByText('e5').closest('td');
			const nf3Cell = screen.getByText('Nf3').closest('td');
			const bc4Cell = screen.getByText('Bc4').closest('td');

			await userEvent.click(e5Cell!);

			// Final question move (e5) should now be active but not clickable.
			expect(e5Cell?.classList.contains('clickable')).toBe(false);
			expect(e5Cell?.classList.contains('active-move')).toBe(true);

			// First answer move (Nf3) should not be active but clickable.
			expect(nf3Cell?.classList.contains('clickable')).toBe(true);
			expect(nf3Cell?.classList.contains('active-move')).toBe(false);

			// Second answer move (Bc4) should not be active but clickable.
			expect(bc4Cell?.classList.contains('clickable')).toBe(true);
			expect(bc4Cell?.classList.contains('active-move')).toBe(false);
		});

		it('allows clicking the other answer move', async () => {
			render(Moves, { pcard: mockCard });

			const e5Cell = screen.getByText('e5').closest('td');
			const nf3Cell = screen.getByText('Nf3').closest('td');
			const bc4Cell = screen.getByText('Bc4').closest('td');

			await userEvent.click(bc4Cell!);

			// Final question move (e5) should not be active but clickable.
			expect(e5Cell?.classList.contains('clickable')).toBe(true);
			expect(e5Cell?.classList.contains('active-move')).toBe(false);

			// First answer move (Nf3) should not be active but clickable.
			expect(nf3Cell?.classList.contains('clickable')).toBe(true);
			expect(nf3Cell?.classList.contains('active-move')).toBe(false);

			// Second answer move (Bc4) should be active but not clickable.
			expect(bc4Cell?.classList.contains('clickable')).toBe(false);
			expect(bc4Cell?.classList.contains('active-move')).toBe(true);
		});
	});
});
