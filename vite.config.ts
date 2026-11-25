import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
	plugins: [svelte()],
	base: command === 'serve' ? '/' : '/_addons/705507113/web',
	build: {
		outDir: 'dist',
		assetsDir: '.',
		rollupOptions: {
			output: {
				entryFileNames: 'bundle.js',
				assetFileNames: '[name].[ext]',
			},
		},
	},
}));
