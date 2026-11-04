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

<main data-theme="dark">
	<header>
		<div class="brand">
			<i class="bi bi-diagram-3-fill"></i>
			<span>Chess Opening Trainer</span>
		</div>
		<div class="theme-toggle-wrapper">
			<i class="bi bi-sun-fill"></i>
			<label class="theme-switch">
				<input type="checkbox" id="theme-toggle-checkbox">
				<span class="slider"></span>
			</label>
			<i class="bi bi-moon-stars-fill"></i>
		</div>
	</header>

	{#if questionImg}
		<img src={questionImg} alt="Question Position" />
	{/if}
	{#if answerImg}
		<img src={answerImg} alt="Answer Position" />
	{/if}
</main>
