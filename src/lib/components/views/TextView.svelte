<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import CodeBlock from '$lib/components/views/CodeBlock.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
</script>

<div class="h-full overflow-y-auto">
  <CodeBlock bind:value={viewStore.textOutput} language="yaml" class="min-h-full" />
</div>
