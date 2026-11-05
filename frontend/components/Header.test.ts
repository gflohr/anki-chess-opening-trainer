import { render, screen } from '@testing-library/svelte';
import { describe, expect, it } from 'vitest';

import Header from './Header.svelte';

describe('Header Component', () => {
	it('renders the brand title', () => {
		render(Header);

		const titleElement = screen.getByText('Chess Opening Trainer');
		expect(titleElement).toBeInTheDocument();
	});

	it('toggles theme state correctly when checkbox changes', () => {
		render(Header, { props: { isLight: false } });

		const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
		expect(checkbox.checked).toBe(false);

		// Simulate user checking the box.
		checkbox.click();
		expect(checkbox.checked).toBe(true);
	});
});
