<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  Local email/password login + signup (backend: routers/auth.py). This is
  what community deployments (no OAuth configured, not a trial build) use
  instead of the OIDC redirect flow in $lib/auth/oauth.ts - see
  initAuth()'s community branch, which sends the browser here when there's
  no valid session token.

  The root layout (+layout.svelte) skips calling initAuth() for this route
  for the same reason it skips it for /auth/callback: this page drives its
  own login (loginWithPassword/signupWithPassword -> initAuth()) and a
  second concurrent initAuth() call would just race it.
-->
<script lang="ts">
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import { loginWithPassword, signupWithPassword, initAuth } from '$lib/auth/oauth';

  let mode: 'login' | 'signup' = $state('login');
  let email = $state('');
  let password = $state('');
  let displayName = $state('');
  let errorMessage = $state('');
  let submitting = $state(false);

  function extractErrorMessage(error: unknown): string {
    // FastAPI's HTTPException(detail=...) lands here as error.response.data.detail.
    const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    return detail || 'Something went wrong. Please try again.';
  }

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    errorMessage = '';
    submitting = true;
    try {
      if (mode === 'login') {
        await loginWithPassword(email, password);
      } else {
        await signupWithPassword(email, password, displayName);
      }
      await initAuth();
      goto('/', { replaceState: true });
    } catch (error) {
      console.error(`${mode} failed:`, error);
      errorMessage = extractErrorMessage(error);
    } finally {
      submitting = false;
    }
  }

  function toggleMode() {
    mode = mode === 'login' ? 'signup' : 'login';
    errorMessage = '';
  }
</script>

<svelte:head>
  <title>{mode === 'login' ? 'Log in' : 'Sign up'} — PeriHub</title>
</svelte:head>

<div class="flex min-h-[70vh] flex-col items-center justify-center gap-6 px-4">
  <Card class="w-full max-w-sm p-6">
    <h1 class="mb-1 text-xl font-semibold">{mode === 'login' ? 'Log in' : 'Create an account'}</h1>
    <p class="text-muted-foreground mb-6 text-sm">
      {mode === 'login' ? 'Welcome back to PeriHub.' : 'Set up your PeriHub account.'}
    </p>

    <form class="flex flex-col gap-4" onsubmit={handleSubmit}>
      {#if mode === 'signup'}
        <div class="flex flex-col gap-1.5">
          <Label for="display-name">Name</Label>
          <Input
            id="display-name"
            type="text"
            bind:value={displayName}
            required
            autocomplete="name"
          />
        </div>
      {/if}

      <div class="flex flex-col gap-1.5">
        <Label for="email">Email</Label>
        <Input id="email" type="email" bind:value={email} required autocomplete="email" />
      </div>

      <div class="flex flex-col gap-1.5">
        <Label for="password">Password</Label>
        <Input
          id="password"
          type="password"
          bind:value={password}
          required
          minlength={mode === 'signup' ? 8 : undefined}
          autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
        />
      </div>

      {#if errorMessage}
        <p class="text-destructive text-sm">{errorMessage}</p>
      {/if}

      <Button type="submit" size="lg" disabled={submitting} class="mt-2">
        {#if submitting}
          {mode === 'login' ? 'Logging in…' : 'Signing up…'}
        {:else}
          {mode === 'login' ? 'Log in' : 'Sign up'}
        {/if}
      </Button>
    </form>

    <button
      type="button"
      onclick={toggleMode}
      class="text-muted-foreground hover:text-foreground mt-4 w-full text-center text-sm underline-offset-4 hover:underline"
    >
      {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Log in'}
    </button>
  </Card>
</div>
