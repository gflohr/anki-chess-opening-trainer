import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import globals from 'globals';

export default tseslint.config(
	eslint.configs.recommended,
	...tseslint.configs.recommended,
	{
		rules: {
			'no-irregular-whitespace': 'off',
			'no-control-regex': 'off',
		},
		languageOptions: {
			globals: {
				...globals.browser,
			},
		},
	},
);
