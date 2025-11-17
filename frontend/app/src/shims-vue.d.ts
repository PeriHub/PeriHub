/* eslint-disable */

// Mocks all files ending in `.vue` showing them as plain Vue instances
import type { Quasar } from 'quasar';
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $q: Quasar;
  }
}

declare module 'vue3-plotly';
declare module 'prismjs/components/prism-core';
declare module 'bibtex-parse-js';
declare module 'vue-vtk-js';
declare module 'vue-chartkick';
declare module 'objleaves';
