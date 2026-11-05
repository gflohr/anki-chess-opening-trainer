import { mount } from 'svelte';
import './app.css';
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
		answers: ['/answer1.svg', '/answer2.svg', '/answer3.svg', '/answer4.svg'],
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
