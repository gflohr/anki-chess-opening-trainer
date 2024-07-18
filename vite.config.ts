import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { viteStaticCopy } from 'vite-plugin-static-copy';

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		svelte(),
		viteStaticCopy({
			targets: [{ src: './assets/css/**/*', dest: 'src' }],
			//flatten: false,
	}),
	],
	build: {
		rollupOptions: {
			input: 'typescript/main.ts',
		},
	},
})
