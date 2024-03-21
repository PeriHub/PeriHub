<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-scroll-area style="height:100%;">
    <prism-editor class="my-editor" v-model="viewStore.textOutput" :highlight="highlighter" line-numbers></prism-editor>
  </q-scroll-area>
</template>

<script>
import { defineComponent } from 'vue'
import { useViewStore } from 'stores/view-store';

import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-yaml";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles
export default defineComponent({
  name: 'TextView',
  components: {
    PrismEditor
  },
  setup() {
    const viewStore = useViewStore();

    return {
      viewStore,
    }
  },
  data() {
    return {
      textHeight: "400px",
    };
  },
  methods: {
    highlighter(code) {
      return highlight(code, languages.yaml); // languages.<insert language> to return html with markup
    },
  },
})
</script>
<style>
/* required class */
.my-editor {
  /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
  background: #2d2d2d;
  color: #ccc;

  /* you must provide font-family font-size line-height. Example: */
  font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 5px;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
  outline: none;
}
</style>
