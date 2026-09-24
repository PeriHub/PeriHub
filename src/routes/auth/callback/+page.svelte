<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  The IdP redirects the browser here after login, with `code` (and `state`,
  echoed back from /oauth/oidc/login) as query params - see
  $lib/auth/oauth.ts's module doc for the full flow.

  The root layout (+layout.svelte) deliberately skips calling initAuth() for
  this route, so this page is responsible for finishing the login itself
  (completeOAuthCallback + initAuth) before it's safe to navigate away.
-->
<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import { completeOAuthCallback, initAuth } from '$lib/auth/oauth';

  let errorMessage = $state('');

  onMount(async () => {
    const params = $page.url.searchParams;
    const idpError = params.get('error');
    const code = params.get('code');
    const state = params.get('state');

    if (idpError) {
      errorMessage = params.get('error_description') || `Login failed: ${idpError}`;
      return;
    }
    if (!code || !state) {
      errorMessage = 'Missing authorization code from the identity provider.';
      return;
    }

    try {
      await completeOAuthCallback(code, state);
      await initAuth();
      goto('/', { replaceState: true });
    } catch (error) {
      console.error('OAuth callback failed:', error);
      errorMessage = 'Login failed. Please try again.';
    }
  });
</script>

<svelte:head>
  <title>Signing in — PeriHub</title>
</svelte:head>

<div class="flex min-h-[70vh] flex-col items-center justify-center gap-4 text-center">
  {#if errorMessage}
    <div class="text-2xl opacity-70">{errorMessage}</div>
    <Button href="/" variant="secondary" size="lg" class="mt-4">Go Home</Button>
  {:else}
    <div class="text-2xl opacity-70">Signing you in…</div>
  {/if}
</div>
