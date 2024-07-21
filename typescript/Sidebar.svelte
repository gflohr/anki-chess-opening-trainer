<script lang="ts">
	import Clock from './Clock.svelte';
	import Movelist from './Movelist.svelte';
</script>

<chess-sidebar>
	<Movelist></Movelist>
	<Clock></Clock>
</chess-sidebar>

<style lang="scss">
chess-sidebar {
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: max-content auto max-content;
}
</style>
