<script lang="ts">
	import Header from './components/Header.svelte';
	import type { Config } from './config.js';

	let { config = {} }: { config?: Partial<Config> } = $props();

	// Theme state lives here, bound to the Header component
	let isLight = $state(false);

	let questionImg = $derived(config.images?.question || '');
	let answerImg = $derived(config.images?.answers?.[0] || '');

	// Apply the theme attribute to the body whenever `isLight` changes
	$effect(() => {
		document.body.setAttribute('data-theme', isLight ? 'light' : 'dark');
	});
</script>

<main>
	<Header bind:isLight />

	{#if questionImg}
		<img src={questionImg} alt="Question Position" />
	{/if}
	{#if answerImg}
		<img src={answerImg} alt="Answer Position" />
	{/if}
</main>
