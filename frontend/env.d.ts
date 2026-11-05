/// <reference types="svelte" />
/// <reference types="vite/client" />

declare module '*.svelte' {
	import type { Component } from 'svelte';

	// biome-ignore lint/suspicious/noExplicitAny: unavoidable
	const component: Component<any>;
	export default component;
}
