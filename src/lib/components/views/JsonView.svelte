<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { JSONEditor, Mode } from 'svelte-jsoneditor';
  import 'svelte-jsoneditor/themes/jse-theme-dark.css';
  import { viewStore } from '$lib/stores/view-store.svelte';
</script>

<div class="jse-theme-dark h-full w-full">
  <JSONEditor
    content={{ json: viewStore.jsonData }}
    readOnly
    mode={Mode.tree}
    mainMenuBar={false}
    navigationBar={false}
    statusBar={false}
  />
</div>
