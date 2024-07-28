<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Board from './Board.svelte';
	import Sidebar from './Sidebar.svelte';
	import { configuration } from './store';
	import { ConfigLoader } from './config-loader';
	import type { Config } from './config';

	let linkElement: HTMLLinkElement;
	const appElement = document.getElementById('app');
	const prefix = appElement?.dataset.prefix;
	const params = new URLSearchParams(document.location.search);

	let baseSize = 512;
	let is3d = false;
	let size: number = 1.0;
	let width = size * baseSize;
	let height = size * baseSize;

	(window as any).chessOpeningTrainerUpdateConfig = (newConfig: string) => {
		configuration.set(JSON.parse(newConfig));
	};

	const resize = () => {
		const mainWrap = document.getElementById('main-wrap');
		if (!mainWrap) return;

		const sidebar = mainWrap.querySelector('chess-sidebar');
		if (!sidebar) return;

		const styles = getComputedStyle(mainWrap);
		const availableWidth =
			mainWrap.clientWidth -
			parseFloat(styles.paddingLeft) -
			parseFloat(styles.paddingRight) -
			parseFloat(styles.borderLeft) -
			parseFloat(styles.borderRight);
		const availableHeight =
			mainWrap.clientHeight -
			parseFloat(styles.paddingTop) -
			parseFloat(styles.paddingBottom) -
			parseFloat(styles.borderTop) -
			parseFloat(styles.borderBottom);

		const sidebarWidth = sidebar.clientWidth;

		if (availableWidth - sidebarWidth < availableHeight) {
			baseSize = availableWidth - sidebarWidth;
		} else {
			baseSize = availableHeight;
		}

		width = size * baseSize;
		if (is3d) {
			height = (958 / 1024) * size * baseSize;
		} else {
			height = size * baseSize;
		}
	};

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
		resize();
	});

	onDestroy(() => unsubscribe);

	onMount(async () => {
		let config: Config;

		if (params.has('config')) {
			config = JSON.parse(params.get('config') as string);
		} else {
			const configLoader = new ConfigLoader(prefix as string);
			config = await configLoader.load();
		}
		configuration.set(config);

		if (!appElement) return;

		const observer = new ResizeObserver(entries => {
			resize();
		});

		observer.observe(appElement);

		return new Promise(resolve => {
			resolve(() => observer.unobserve(appElement));
		});
	});
</script>

<chess-opening-trainer
	style="grid-template-columns:{width}px {width /
		2}px; grid-template-rows:{height}px;"
>
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
