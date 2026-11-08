<script lang="ts">
	interface Props {
		isLight?: boolean;
		analyseLink: string | null;
	};

	let {
		isLight = $bindable(false),
		analyseLink = $bindable(null)
	}: Props = $props();

	function handleLichessClick(event: MouseEvent) {
		if (!analyseLink) {
			event.preventDefault();
		}
	}
</script>

<header>
	<div class="brand">
		<i class="bi bi-diagram-3-fill"></i>
		<span>Chess Opening Trainer</span>
	</div>

	<div class="header-right">
		<div class="social-links">
			<a
				href="https://github.com/gflohr/anki-chess-opening-trainer#readme"
				target="_blank"
				rel="noopener noreferrer"
				title="Source Code on GitHub"
			>
				<i class="bi bi-github"></i>
			</a>
			<a
				href="https://www.guido-flohr.net/practice-chess-openings-with-anki/"
				target="_blank"
				rel="noopener noreferrer"
				title="Documentation"
			>
				<i class="bi bi-book"></i>
			</a>
			<a
				href="https://ankiweb.net/shared/info/705507113"
				target="_blank"
				rel="noopener noreferrer"
				title="Add-on Page"
			>
				<i class="bi bi-lightbulb"></i>
			</a>
			<a
				href={analyseLink ?? '#'}
				target={analyseLink ? "_blank" : undefined}
				rel={analyseLink ? "noopener noreferrer" : undefined}
				title={analyseLink ? "Analyse in Lichess" : "Analysis unavailable on question side"}
				class:disabled={!analyseLink}
				onclick={handleLichessClick}
			>
				<span class="lichess-icon"></span>
			</a>		</div>
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
