import { mount } from 'svelte';
import './app.css';
import App from './App.svelte';
import { type Config, type RawConfig, translateRawConfig } from './config.js';

// Declare global config type for TypeScript
declare global {
	interface Window {
		config?: Config | RawConfig;
	}
}

// Fallback config for local development only
const devConfig: RawConfig = {
	i: {
		q: '/question.svg',
		a: ['/answer1.svg', '/answer2.svg', '/answer3.svg', '/answer4.svg'],
	},
	s: {
		m: [
			{ s: 'e4' },
			{ s: 'e5' },
			{ s: 'Nf3' },
			{ s: 'Nc6' },
			{ s: 'Bc4' },
			{ s: 'Nf6' },
			{ s: 'Ng5' },
			{ s: 'd5' },
			{ s: 'exd5' },
		],
		a: [{ s: 'b5' }, { s: 'Na5' }],
	},
	c: ['This is the Italian Game.', 'It is also known as Giuco Piano.'],
};

const targetElement = document.getElementById('app')!;

try {
	// Use window.config if injected by Anki/importer, otherwise fallback to devConfig
	const rawConfig = window.config || (import.meta.env.DEV ? devConfig : {});
	const config = translateRawConfig(rawConfig);

	mount(App, {
		target: targetElement,
		props: {
			config,
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
                    <i class="bi bi-exclamation-triangle-fill"></i> Configuration Error
                </h3>
                <p style="color: #9aa0a6; font-size: 0.9rem; line-height: 1.5; margin: 0 0 16px 0; word-break: break-word;">
                    ${message}
                </p>
                <p style="color: #6b7280; font-size: 0.75rem; margin: 0;">
                    Please check your card template or JSON data payload.
                </p>
            </div>
        </div>
    `;
}
