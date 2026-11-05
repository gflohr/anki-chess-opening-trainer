<script lang="ts">
	let { isLight = $bindable(false) }: { isLight?: boolean } = $props();
</script>

<header>
	<div class="brand">
		<i class="bi bi-diagram-3-fill"></i>
		<span>Chess Opening Trainer</span>
	</div>
	<div class="theme-toggle-wrapper">
		<i class="bi bi-sun-fill"></i>
		<label class="theme-switch">
			<input type="checkbox" bind:checked={isLight} />
			<span class="slider"></span>
		</label>
		<i class="bi bi-moon-stars-fill"></i>
	</div>
</header>
