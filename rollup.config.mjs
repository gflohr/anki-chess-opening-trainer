import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';
import copy from 'rollup-plugin-copy';
import sass from 'rollup-plugin-sass';
import postcss from 'postcss';
import cssnano from 'cssnano';
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
			sourcemap: true,
		},
		plugins: [
			resolve(),
			commonjs(),
			typescript({
				exclude: 'src/**/*.spec.ts',
			}),
			sass({
				output: 'src/assets/bundle.css',
			}),
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
			sass({
				output: function (styles) {
					// Process and minify CSS using postcss and cssnano
					return postcss([cssnano])
						.process(styles, { from: undefined })
						.then(result => {
							fs.writeFileSync('src/assets/bundle.min.css', result.css);
						});
				},
			}),
			// We only have to copy the files once.
			copy({
				targets: [{ src: './assets/**/*', dest: 'src' }],
				flatten: false,
			}),
			terser(),
		],
		watch: {
			include: ['./typescript/**/*.ts'],
			exclude: ['./typescript/**/*.spec.ts'],
		},
	},
];
