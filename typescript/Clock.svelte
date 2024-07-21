<script lang="ts">
	import { onMount } from 'svelte';

	let hours = 0;
	let minutes = 0;
	let seconds = 0;
	let tenths = 0;
	let running = false;
	let started: Date = new Date();
	let interval = setInterval(updateTime, 100);

	function updateTime() {
		const now = new Date();

		let elapsed = now.getTime() - started.getTime();

		hours = Math.floor(elapsed / (1000 * 60 * 60));
		elapsed -= hours * 1000 * 60 * 60;

		minutes = Math.floor(elapsed / (1000 * 60));
		elapsed -= minutes * 1000 * 60;

		seconds = Math.floor(elapsed / 1000);
		elapsed -= seconds * 1000;

		tenths = Math.floor(elapsed / 100);
	}

	onMount(() => {
		return () => {
			clearInterval(interval);
		};
	});

	function formatNumber(number: number, digits = 2) {
		return number.toString().padStart(digits, '0');
	}
</script>

<chess-clock>
	<svg
		xmlns="http://www.w3.org/2000/svg"
		viewBox="0 0 24 24"
		width="48px"
		height="48px"
	>
		<circle
			cx="12"
			cy="12"
			r="9"
			stroke="black"
			stroke-width="1.5"
			fill="none"
		/>
		<polyline
			points="12,6 12,12 16,16"
			stroke="black"
			stroke-width="1.5"
			fill="none"
		/>
	</svg>
	<div class="digits">
		<div>{formatNumber(hours)}:</div>
		<div>{formatNumber(minutes)}:</div>
		<div>{formatNumber(seconds)}.</div>
		<div>{tenths}</div>
	</div>
</chess-clock>

<style>
	chess-clock {
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: #eee;
		font-size: 18pt;
		padding: 0.5rem;
	}
	.digits {
		display: flex;
	}
	.digits div {
		margin: 0 2px;
	}
</style>
