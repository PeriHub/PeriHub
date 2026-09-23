// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { readFileSync } from 'node:fs';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type Plugin } from 'vite';

// vtk.js imports its WebGL/WebGPU shaders as raw source, e.g.
// `import src from './foo.glsl'`, expecting the file's text content back.
// Neither esbuild's dependency pre-bundler nor Vite/Rollup know that
// extension out of the box, so without this, dev startup fails with
// "No loader is configured for '.glsl' files" the moment vtk.js (opted
// into optimizeDeps below) is first pre-bundled.
function glslAsText(): Plugin {
  const glslRe = /\.glsl$/;
  return {
    name: 'vtkjs-glsl-as-text',
    enforce: 'pre',
    load(id) {
      if (glslRe.test(id)) {
        return `export default ${JSON.stringify(readFileSync(id, 'utf-8'))};`;
      }
    }
  };
}

export default defineConfig({
  plugins: [tailwindcss(), sveltekit(), glslAsText()],
  server: {
    port: 9000,
    watch: {
      // The FastAPI backend appends to this log file on every API request
      // (including simulation start/cancel). It lives inside the project
      // root, so without this Vite's watcher treats every write as a
      // source change it can't HMR and triggers a full page reload.
      ignored: ['**/backend/**']
    },
    proxy: {
      // Mirrors the old Quasar dev proxy to the FastAPI backend.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  optimizeDeps: {
    include: ['vtk.js'],
    esbuildOptions: {
      // Same fix as glslAsText() above, but for esbuild's own dependency
      // pre-bundling scan, which runs outside Vite's plugin pipeline.
      loader: { '.glsl': 'text' }
    }
  }
});
