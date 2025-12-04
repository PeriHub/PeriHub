<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="my-json-editor jse-theme-dark">
    <vue-json-pretty :data="viewStore.jsonData" />
    <!-- <JsonEditorVue v-model="viewStore.jsonData" :mainMenuBar=false :navigationBar=false :statusBar=false :readOnly=true
      v-bind="{/* local props & attrs */ }" /> -->
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useViewStore } from 'src/stores/view-store';
// import JsonEditorVue from 'json-editor-vue'
import VueJsonPretty from 'vue-json-pretty';
export default defineComponent({
  name: 'JsonView',
  components: {
    VueJsonPretty
    // JsonEditorVue
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
