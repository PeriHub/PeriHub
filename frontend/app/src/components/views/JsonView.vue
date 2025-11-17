<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="my-json-editor jse-theme-dark">
    <JsonEditorVue v-model="viewStore.jsonData" mode="tree" :mainMenuBar=false :navigationBar=false :statusBar=false
      :readOnly=true v-bind="{/* local props & attrs */ }" />
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { useViewStore } from 'src/stores/view-store';
import JsonEditorVue from 'json-editor-vue'
export default defineComponent({
  name: 'JsonView',
  components: {
    JsonEditorVue
  },
  setup() {
    const viewStore = useViewStore();

    return {
      viewStore,
    }
  },
})
</script>

<style>
/* load one or multiple themes */
@import 'svelte-jsoneditor/themes/jse-theme-dark.css';
</style>
