/* eslint-disable */

// Mocks all files ending in `.vue` showing them as plain Vue instances
import type { Quasar } from 'quasar';
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
// declare module '*.vue.esm-bundler.js' {
//   // Re‑export everything from the real Vue module
//   export * from 'vue';
//   // Keep the default export as the Vue constructor
//   export { default } from 'vue';
// }
declare module '*.vue.esm-bundler.js' {
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
