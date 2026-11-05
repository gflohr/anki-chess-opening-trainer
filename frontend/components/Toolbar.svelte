<script lang="ts">
	interface Props {
		isBoardHidden: boolean;
		onToggleBoard: () => void;
	}

	let { isBoardHidden = $bindable(false), onToggleBoard }: Props = $props();

	// Reactive state to track whether the settings popover is open
	let showSettings = $state(false);

	function toggleSettings(e: MouseEvent) {
		e.stopPropagation();
		showSettings = !showSettings;
	}

	// Close settings when clicking anywhere outside the container
	function closeSettings() {
		showSettings = false;
	}
</script>

<svelte:window onclick={closeSettings} />

<!-- Toolbar Below Moves -->
<div class="moves-toolbar">
	<div class="nav-buttons">
		<button class="icon-btn" title="Go to start"><i class="bi bi-skip-backward"></i></button>
		<button class="icon-btn" title="Previous move"><i class="bi bi-rewind"></i></button>
		<button class="icon-btn" title="Next move"><i class="bi bi-fast-forward"></i></button>
		<button class="icon-btn" title="Go to end"><i class="bi bi-skip-forward"></i></button>
	</div>

	<!-- Wrapper that stops propagation so clicking inside the settings menu doesn't trigger the window closer -->
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="settings-wrapper" onclick={(e) => e.stopPropagation()}>
		<button
			class="icon-btn"
			id="settings-btn"
			title="Settings"
			onclick={toggleSettings}
		>
			<i class="bi bi-chevron-up chevron-icon"></i>
		</button>

		<!-- Settings Dialog bound reactively via class:active -->
		<div class="settings-dialog" class:active={showSettings}>
			<button onclick={() => { onToggleBoard(); showSettings = false; }}>
				<i class="bi {isBoardHidden ? 'bi-eye' : 'bi-eye-slash'}"></i>
				{isBoardHidden ? 'Show Board' : 'Hide Board'}
			</button>
		</div>
	</div>
</div>
