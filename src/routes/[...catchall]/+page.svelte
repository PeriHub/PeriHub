<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!-- Catch-all 404, replaces pages/ErrorNotFound.vue -->
<script lang="ts">
  import Button from '$lib/components/ui/Button.svelte';
</script>

<svelte:head>
  <title>404 — PeriHub</title>
</svelte:head>

<div
  class="flex min-h-[70vh] flex-col items-center justify-center gap-4 bg-primary px-6 text-center text-primary-foreground"
>
  <div class="text-[20vh] font-bold leading-none">404</div>
  <div class="text-2xl opacity-70">Oops. Nothing here...</div>
  <Button href="/" variant="secondary" size="lg" class="mt-4">Go Home</Button>
</div>
