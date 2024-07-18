<script lang="ts">
	import { onMount } from 'svelte';
	import clockLogo from '/images/clock.svg';

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
		const elapsed0 = elapsed;

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
	<img src={clockLogo} width="48px" height="48px" alt="Clock" />
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
		font-family: sans-serif;
		font-size: 2em;
		align-items: center;
		justify-content: center;
	}
	.digits {
		display: flex;
	}
	.digits div {
		margin: 0 2px;
	}
</style>
