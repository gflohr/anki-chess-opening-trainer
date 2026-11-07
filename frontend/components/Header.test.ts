import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import Header from './Header.svelte';

describe('Header Component', () => {
	it('renders the brand title', () => {
		render(Header);

		const titleElement = screen.getByText('Chess Opening Trainer');
		expect(titleElement).toBeInTheDocument();
	});

	it('toggles theme state and reflects external prop changes', async () => {
		const user = userEvent.setup();
		const { rerender } = render(Header, { props: { isLight: false } });

		const checkbox = screen.getByRole('checkbox') as HTMLInputElement;
		expect(checkbox.checked).toBe(false);

		// Simulate a real user clicking the toggle
		await user.click(checkbox);
		expect(checkbox.checked).toBe(true);

		// Verify that if an external source (like Anki config) updates the prop, the UI syncs
		await rerender({ isLight: false });
		expect(checkbox.checked).toBe(false);
	});
});
