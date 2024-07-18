<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Board from './Board.svelte';
	import Sidebar from './Sidebar.svelte';
	import { configuration } from './store';
	import { ConfigLoader } from './config-loader';

	let linkElement: HTMLLinkElement;
	const appElement = document.getElementById('app');
	let rawLine = appElement?.dataset.line;
	const prefix = appElement?.dataset.prefix;

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

<chess-opening-trainer>
	<Board></Board>
	<Sidebar></Sidebar>
</chess-opening-trainer>
