import { mount } from 'svelte';
import './app.css';
import { commitValueAfterInput } from '@testing-library/user-event/dist/cjs/document/trackValue.js';
import App from './App.svelte';
import type { Config } from './config.js';

// Declare global config type for TypeScript
declare global {
	interface Window {
		config?: Config;
	}
}

// Fallback config for local development only
const devConfig: Config = {
	images: {
		question: '/question.svg',
		answers: [
			'/answer1.svg',
			'/answer2.svg',
			'/answer3.svg',
			'/answer4.svg',
		],
	},
	session: {
		game: {
			gameAnnotations: {
				comments: [
					'This is the Italian Game.',
					'It is also known as Giuco Piano.',
				],
			},
			questionMoves: [
				{ san: 'e4' },
				{ san: 'e5' },
				{ san: 'Nf3' },
				{ san: 'Nc6' },
				{ san: 'Bc4' },
				{ san: 'Nf6' },
				{ san: 'Ng5' },
				{ san: 'd5' },
				{ san: 'exd5' },
			],
			answerMoves: [{ san: 'b5' }, { san: 'Na5' }],
		},
	},
};

// Use window.config if injected by Anki/importer, otherwise fallback to devConfig
const config = window.config || (import.meta.env.DEV ? devConfig : {});

const app = mount(App, {
	target: document.getElementById('app')!,
	props: {
		config,
	},
});

export default app;
