import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';
import * as fs from 'fs';

const pkg = JSON.parse(
	fs.readFileSync('./package.json', { encoding: 'utf-8' }),
);

export default [
	// UMD builds for the browser.
	{
		input: 'typescript/index.ts',
		output: {
			name: 'ankichess',
			file: pkg.browser,
			format: 'umd',
			sourcemap: false,
		},
		plugins: [
			resolve(),
			commonjs(),
			typescript({
				exclude: 'src/**/*.spec.ts',
			}),
			terser(),
		],
	},
	{
		input: 'typescript/index.ts',
		output: {
			name: 'ankichess',
			file: pkg.browser.replace(/\.js$/, '.min.js'),
			format: 'umd',
			sourcemap: true,
		},
		plugins: [
			resolve(),
			commonjs(),
			typescript({
				exclude: 'src/**/*.spec.ts',
			}),
		],
	},
];
