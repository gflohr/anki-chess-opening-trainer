import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

// https://vite.dev/config/
export default defineConfig({
	plugins: [svelte()],
	base: '/',
	build: {
		outDir: 'dist',
		assetsDir: '.',
		rollupOptions: {
			output: {
				entryFileNames: '_chess_opening_trainer_bundle.js',
				assetFileNames: '_chess_opening_trainer_[name].[ext]',
			},
		},
	},
});
