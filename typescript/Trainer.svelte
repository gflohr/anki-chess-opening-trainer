<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Board from './Board.svelte';
	import Sidebar from './Sidebar.svelte';
	import { configuration } from './store';
	import { ConfigLoader } from './config-loader';

	let linkElement: HTMLLinkElement;
	const appElement = document.getElementById('app');
	const prefix = appElement?.dataset.prefix;

	// FIXME! Calculate that based on the available space!
	let baseSize = 512;
	let is3d = false;
	let size: number = 1.0;
	let width = size * baseSize;
	let height = size * baseSize;

	const recomputeDimensions = (is3d: boolean) => {
		if (is3d) {
			height = 958 / 1024 * size * baseSize;
		} else {
			height = size * baseSize;
		}
	}

	const unsubscribe = configuration.subscribe(config => {
		if (!config) {
			return;
		}

		const pieces2D = config.board['2Dpieces'];
		const linkUrl = `${prefix}/assets/css/pieces/${pieces2D}.css`;
		if (!linkElement) {
			linkElement = document.createElement('link');
			linkElement.rel = 'stylesheet';
			document.head.appendChild(linkElement);
		}
		linkElement.href = linkUrl;

		is3d = config.board['3D'];
		recomputeDimensions(is3d);
	});

	onDestroy(() => {
		unsubscribe();
	});

	onMount(async () => {
		const configLoader = new ConfigLoader(prefix as string);
		const config = await configLoader.load();
		configuration.set(config);
	});
</script>

<chess-opening-trainer
	style="grid-template-columns:{width}px auto; grid-template-rows:{height}px;">
	<Board></Board>
	<Sidebar></Sidebar>
</chess-opening-trainer>

<style>
chess-opening-trainer {
	position: relative;
	display: grid;
	justify-content: center;
	justify-items: stretch;
	align-items: stretch;
}
</style>
