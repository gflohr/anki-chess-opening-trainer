import { writable } from 'svelte/store';
import { type Config } from './config';

export const configuration = writable<Config | undefined>();
