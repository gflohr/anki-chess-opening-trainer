<script lang="ts">
	let { isLight = $bindable(false) }: { isLight?: boolean } = $props();
</script>

<header>
	<div class="brand">
		<i class="bi bi-diagram-3-fill"></i>
		<span>Chess Opening Trainer</span>
	</div>

	<div class="header-right">
		<div class="social-links">
			<a href="https://github.com/gflohr/anki-chess-opening-trainer#readme" target="_blank" rel="noopener noreferrer" title="Source Code on GitHub">
				<i class="bi bi-github"></i>
			</a>
			<a href="https://www.guido-flohr.net/practice-chess-openings-with-anki/" target="_blank" rel="noopener noreferrer" title="Documentation">
				<i class="bi bi-book"></i>
			</a>
			<a href="https://ankiweb.net/shared/info/705507113" target="_blank" rel="noopener noreferrer" title="Add-on Page">
				<i class="bi bi-lightbulb"></i>
			</a>
			<a href="https://lichess.org/analysis/pgn/1.%20d4%20d5%202.%20c4%20c6%203.%20Nc3%20dxc4%20%2A" target="_blank" rel="noopener noreferrer" title="Analyse in Lichess">
				<span class="lichess-icon"></span>
			</a>
		</div>
		<div class="theme-toggle-wrapper">
			<i class="bi bi-sun-fill"></i>
			<label class="theme-switch">
				<input type="checkbox" bind:checked={isLight} />
				<span class="slider"></span>
			</label>
			<i class="bi bi-moon-stars-fill"></i>
		</div>
	</div>
</header>
