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
	i: {
		q: '/question.svg',
		a: ['/answer1.svg', '/answer2.svg', '/answer3.svg', '/answer4.svg', '/answer5.svg'],
	},
	s: {
		m: [
			[{ s: 'e4', n: 1 }],
			[{ s: 'e5', n: 2 }],
			[{ s: 'Nf3', n: 3 }],
			[{ s: 'Nc6', n: 4 }],
			[{ s: 'Bc4', n: 5 }],
			[{ s: 'Nf6', n: 6 }],
			[{ s: 'Ng5', n: 7 }],
			[{ s: 'd5', n: 8 }],
			[{ s: 'exd5' }],
		],
		a: [
			{ s: 'b5' },
			{ s: 'Na5' },
			{ s: 'Nd4' },
			{ s: 'Nxd5' },
			{ s: 'Nb4' },
		],
	},
	c: ['This is the Italian Game.', 'It is also known as Giuco Piano.'],
};

const targetElement = document.getElementById('app')!;

try {
	alert('loaded')
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
