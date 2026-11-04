<script lang="ts">
	import type { Config } from './config.js';

	// 1. Define component props using Svelte 5's $props() rune
	// We use Partial<Config> because config might be empty/loading initially
	let { config = {} }: { config?: Partial<Config> } = $props();

	// 2. Safely access nested properties using optional chaining (?.)
	// and Svelte 5's $derived rune for reactivity
	let questionImg = $derived(config.images?.question || '');
	let answerImg = $derived(config.images?.answers?.[0] || '');
</script>

<main class="trainer-container">
	{#if questionImg}
		<img src={questionImg} alt="Question Position" />
	{/if}
	{#if answerImg}
		<img src={answerImg} alt="Answer Position" />
	{/if}
</main>
