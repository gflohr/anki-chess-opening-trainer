import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, it, vi } from 'vitest';
import Toolbar from './Toolbar.svelte';

function renderToolbar(
	overrides: Partial<{
		isBoardHidden: boolean;
		canGoBackwards: boolean;
		canGoForward: boolean;
		onToggleBoard: () => void;
		onNavigate: (action: 'start' | 'previous' | 'next' | 'end') => void;
	}> = {},
) {
	const props = {
		isBoardHidden: false,
		canGoBackwards: true,
		canGoForward: true,
		onToggleBoard: vi.fn(),
		onNavigate: vi.fn(),
		...overrides,
	};

	const view = render(Toolbar, { props });
	return { ...view, props };
}

describe('Toolbar Component', () => {
	describe('Toggle Board Visibility', () => {
		it('should initially have the board visible and settings closed', () => {
			const { container } = renderToolbar({ isBoardHidden: false });

			const dialog = container.querySelector('.settings-dialog');
			expect(dialog).not.toHaveClass('active');

			const toggleButton = screen.getByRole('button', {
				name: /hide board/i,
			});
			expect(toggleButton).toBeInTheDocument();
		});

		it('should open settings, invoke onToggleBoard, and close settings when toggled', async () => {
			const { container, props } = renderToolbar({
				isBoardHidden: false,
			});

			const settingsButton = screen.getByTitle('Settings');
			await fireEvent.click(settingsButton);

			const dialog = container.querySelector('.settings-dialog');
			expect(dialog).toHaveClass('active');

			const toggleButton = screen.getByRole('button', {
				name: /hide board/i,
			});
			await fireEvent.click(toggleButton);

			expect(props.onToggleBoard).toHaveBeenCalledTimes(1);
			expect(dialog).not.toHaveClass('active');
		});

		it('should show "Show Board" label when isBoardHidden is true', async () => {
			renderToolbar({ isBoardHidden: true });

			await fireEvent.click(screen.getByTitle('Settings'));

			expect(
				screen.getByRole('button', { name: /show board/i }),
			).toBeInTheDocument();
		});

		it('should close the settings dialog when clicking outside', async () => {
			const { container } = renderToolbar();

			await fireEvent.click(screen.getByTitle('Settings'));
			const dialog = container.querySelector('.settings-dialog');
			expect(dialog).toHaveClass('active');

			await fireEvent.click(window);
			expect(dialog).not.toHaveClass('active');
		});
	});

	describe('Navigation Controls', () => {
		it('should call onNavigate with the expected action when buttons are enabled', async () => {
			const { props } = renderToolbar({
				canGoBackwards: true,
				canGoForward: true,
			});

			await fireEvent.click(screen.getByTitle('Go to start'));
			await fireEvent.click(screen.getByTitle('Previous move'));
			await fireEvent.click(screen.getByTitle('Next move'));
			await fireEvent.click(screen.getByTitle('Go to end'));

			expect(props.onNavigate).toHaveBeenNthCalledWith(1, 'start');
			expect(props.onNavigate).toHaveBeenNthCalledWith(2, 'previous');
			expect(props.onNavigate).toHaveBeenNthCalledWith(3, 'next');
			expect(props.onNavigate).toHaveBeenNthCalledWith(4, 'end');
		});

		it('should disable navigation buttons according to canGoBackwards and canGoForward', () => {
			renderToolbar({
				canGoBackwards: false,
				canGoForward: false,
			});

			expect(screen.getByTitle('Go to start')).toBeDisabled();
			expect(screen.getByTitle('Previous move')).toBeDisabled();
			expect(screen.getByTitle('Next move')).toBeDisabled();
			expect(screen.getByTitle('Go to end')).toBeDisabled();
		});
	});
});
