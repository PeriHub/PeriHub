<!--
  Target of the "forgot password" email (backend: routers/auth.py's
  POST /auth/password/forgot builds the link from PUBLIC_URL). Needs no
  session - the root layout skips initAuth() here, like for /auth/login.
-->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import { resetPasswordWithToken } from '$lib/auth/oauth';
  import { notify } from '$lib/utils/notify';

  const token = page.url.searchParams.get('token') ?? '';
  let password = $state('');
  let repeat = $state('');
  let errorMessage = $state('');
  let submitting = $state(false);
  const mismatch = $derived(repeat !== '' && password !== repeat);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    errorMessage = '';
    submitting = true;
    try {
      await resetPasswordWithToken(token, password);
      notify.positive('Password changed - log in with your new password');
      goto('/auth/login', { replaceState: true });
    } catch (error) {
      errorMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Something went wrong. Please try again.';
    } finally {
      submitting = false;
    }
  }
</script>

<svelte:head>
  <title>Set a new password — PeriHub</title>
</svelte:head>

<div class="flex min-h-[70vh] flex-col items-center justify-center gap-6 px-4">
  <Card class="w-full max-w-sm p-6">
    <h1 class="mb-1 text-xl font-semibold">Set a new password</h1>
    {#if !token}
      <p class="text-muted-foreground text-sm">
        This link is incomplete. Request a new one from the
        <a href="/auth/login" class="underline underline-offset-4">log in page</a>.
      </p>
    {:else}
      <p class="text-muted-foreground mb-6 text-sm">Choose a password of at least 8 characters.</p>
      <form class="flex flex-col gap-4" onsubmit={handleSubmit}>
        <div class="flex flex-col gap-1.5">
          <Label for="new-password">New password</Label>
          <Input
            id="new-password"
            type="password"
            bind:value={password}
            required
            minlength={8}
            autocomplete="new-password"
          />
        </div>
        <div class="flex flex-col gap-1.5">
          <Label for="repeat-password">Repeat new password</Label>
          <Input
            id="repeat-password"
            type="password"
            bind:value={repeat}
            required
            autocomplete="new-password"
          />
        </div>
        {#if mismatch}
          <p class="text-destructive text-sm">The passwords don't match.</p>
        {/if}
        {#if errorMessage}
          <p class="text-destructive text-sm">{errorMessage}</p>
        {/if}
        <Button
          type="submit"
          size="lg"
          disabled={submitting || mismatch || password.length < 8}
          class="mt-2"
        >
          {submitting ? 'Saving…' : 'Set new password'}
        </Button>
      </form>
    {/if}
  </Card>
</div>
