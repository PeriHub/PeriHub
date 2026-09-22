// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),

  kit: {
    // Static adapter: PeriHub ships the built frontend behind nginx (see nginx.conf),
    // so we pre-render a static SPA shell exactly like the old `quasar build` output.
    adapter: adapter({
      pages: 'dist',
      assets: 'dist',
      fallback: 'index.html',
      precompress: false,
      strict: false
    }),
    alias: {
      $lib: 'src/lib',
      'lib/*': 'src/lib/*'
    },
    csp: {
      directives: {
        'script-src': ['self']
      },
      // must be specified with either the `report-uri` or `report-to` directives, or both
      reportOnly: {
        'script-src': ['self'],
        'report-uri': ['/']
      }
    }
  }
};

export default config;
