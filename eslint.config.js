// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import js from '@eslint/js';
import ts from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default ts.config(
  js.configs.recommended,
  ...ts.configs.recommended,
  ...svelte.configs['flat/recommended'],
  prettier,
  ...svelte.configs['flat/prettier'],
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.node }
    }
  },
  {
    files: ['**/*.svelte'],
    languageOptions: {
      parserOptions: {
        parser: ts.parser,
        extraFileExtensions: ['.svelte']
      }
    }
  },
  {
    // Generated OpenAPI client: not worth linting to our style, and it's regenerated anyway.
    ignores: [
      'src/lib/client/**',
      '.svelte-kit/**',
      'dist/**',
      'build/**',
      'node_modules/**',
      'playwright-report/**',
      'test-results/**'
    ]
  },
  {
    rules: {
      // The generated client and several ported components deliberately use `any`
      // at integration boundaries (Plotly/VTK/Prism globals, API error shapes).
      '@typescript-eslint/no-explicit-any': 'warn',
      'svelte/no-unused-svelte-ignore': 'warn',
      // `valid-compile` also surfaces Svelte *compiler warnings* (not just errors)
      // by default - including custom_element_props_identifier, which only matters
      // for components compiled as custom elements (<svelte:options customElement>).
      // This app doesn't ship custom elements, so it fires as noise on every
      // ordinary wrapper component that forwards attrs via `...rest` in $props()
      // (Input, and other ui/* components using the same pattern). Keep the rule
      // for genuine compile errors, ignore compiler warnings.
      'svelte/valid-compile': ['error', { ignoreWarnings: true }]
    }
  }
);
