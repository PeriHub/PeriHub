<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!-- Shown to anonymous visitors and guests on account-only pages: what an account unlocks + sign up / log in. -->
<script lang="ts">
  import { Lock } from 'lucide-svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { publicConfig } from '$lib/config';

  let { title, points, next }: { title: string; points: string[]; next: string } = $props();

  const href = (mode: 'signup' | 'login') =>
    `/auth/login?mode=${mode}&next=${encodeURIComponent(next)}`;
  const button = 'inline-flex h-9 items-center rounded-md px-4 text-sm font-medium no-underline';
</script>

<section class="border-border bg-card mt-10 max-w-xl rounded-xl border p-6">
  <h2 class="flex items-center gap-2 text-lg font-semibold">
    <Lock class="text-muted-foreground h-5 w-5" aria-hidden="true" />
    {title}
  </h2>
  <ul class="text-muted-foreground mt-3 list-disc space-y-1 pl-5 text-sm">
    {#each points as point (point)}
      <li>{point}</li>
    {/each}
  </ul>
  <div class="mt-5 flex flex-wrap gap-2">
    {#if publicConfig.signupOpen}
      <a href={href('signup')} class="{button} bg-primary text-primary-foreground hover:opacity-90">
        Create account
      </a>
    {/if}
    <a
      href={href('login')}
      class="{button} {publicConfig.signupOpen
        ? 'border-input border'
        : 'bg-primary text-primary-foreground hover:opacity-90'}"
    >
      Log in
    </a>
  </div>
  {#if !publicConfig.signupOpen}
    <p class="text-muted-foreground mt-3 text-xs">
      Sign-up is currently closed. Ask an administrator for an account.
    </p>
  {/if}
  {#if authStore.isGuest && publicConfig.signupOpen}
    <p class="text-muted-foreground mt-3 text-xs">
      Work from this guest session isn't carried over to the new account.
    </p>
  {/if}
</section>
