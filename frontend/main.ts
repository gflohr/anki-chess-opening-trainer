import { mount } from 'svelte';
import './app.css';
import App from './App.svelte';
import { type Card, type RawCard, translateRawCard } from './domain/card.js';

// Declare global card type for TypeScript.
declare global {
	interface Window {
		card?: Card | RawCard;
	}
}

// Fallback card for local development only.
const devCard: RawCard = {
	i: [
		'/chess-opening-trainer-initial.svg',
		'/chess-opening-trainer-e4.svg',
		'/chess-opening-trainer-e5.svg',
		'/chess-opening-trainer-Nf3.svg',
		'/chess-opening-trainer-Nc6.svg',
		'/chess-opening-trainer-Bc4.svg',
		'/chess-opening-trainer-Nf6.svg',
		'/chess-opening-trainer-Ng5.svg',
		'/chess-opening-trainer-d5.svg',
		'/chess-opening-trainer-exd5.svg',
		'/chess-opening-trainer-b5.svg',
		'/chess-opening-trainer-Na5.svg',
		'/chess-opening-trainer-Nd4.svg',
		'/chess-opening-trainer-Nxd5.svg',
		'/chess-opening-trainer-Nb4.svg',
	],
	s: {
		m: [
			[{ s: 'e4', i: 1, n: 1 }],
			[{ s: 'e5', i: 2, n: 2 }],
			[{ s: 'Nf3', i: 3, n: 3 }],
			[{ s: 'Nc6', i: 4, n: 4 }],
			[{ s: 'Bc4', i: 5, n: 5 }],
			[{ s: 'Nf6', i: 6, n: 6 }],
			[{ s: 'Ng5', i: 7, n: 7 }],
			[{ s: 'd5', i: 8, n: 8 }],
			[{ s: 'exd5', i: 9 }],
		],
		a: [
			{ s: 'b5', i: 10 },
			{ s: 'Na5', i: 11 },
			{ s: 'Nd4', i: 12 },
			{ s: 'Nxd5', i: 13 },
			{ s: 'Nb4', i: 14 },
		],
	},
	c: ['This is the Italian Game.', 'It is also known as Giuco Piano.'],
};

const targetElement = document.getElementById('app')!;

try {
	// Use window.card if injected by Anki/importer, otherwise fallback to devCard
	const rawCard = window.card || (import.meta.env.DEV ? devCard : {});
	const card = translateRawCard(rawCard);
	//card.isQuestion = true;

	mount(App, {
		target: targetElement,
		props: {
			card,
		},
	});
} catch (error) {
	// Extract a clean error message
	const message = error instanceof Error ? error.message : String(error);

	// Render a high-visibility error card directly into the Anki WebView
	targetElement.innerHTML = `
		<div style="
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			height: 100vh;
			padding: 24px;
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
			background-color: #121418;
			color: #f0f2f5;
			text-align: center;
			box-sizing: border-box;
		">
			<div style="
				background-color: #1e222a;
				border: 1px solid #da3633;
				border-radius: 8px;
				padding: 24px;
				max-width: 500px;
				width: 100%;
				box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
			">
				<h3 style="color: #da3633; margin-top: 0; margin-bottom: 12px; font-size: 1.2rem;">
					<i class="bi bi-exclamation-triangle-fill"></i> Internal Error - Corrupt Card
				</h3>
				<p style="color: #9aa0a6; font-size: 0.9rem; line-height: 1.5; margin: 0 0 16px 0; word-break: break-word;">
					${message}
				</p>
				<p style="color: #6b7280; font-size: 0.75rem; margin: 0;">
					Please check your card template or JSON data payload!
				</p>
			</div>
		</div>
	`;
}
