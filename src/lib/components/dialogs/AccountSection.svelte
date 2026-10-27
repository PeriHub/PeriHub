<script lang="ts">
  import { changePassword, deleteAccount, updateAccountSettings } from '$lib/client';
  import type { MeResponse } from '$lib/client';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { publicConfig } from '$lib/config';
  import { notify } from '$lib/utils/notify';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';

  let { profile }: { profile: MeResponse } = $props();

  // OAuth accounts have no PeriHub password: no change, and deletion is confirmed by typing the email.
  const hasPassword = $derived(profile.auth_provider === 'local');
  // How deletion is confirmed: password, else the account's email, else typing DELETE.
  const confirmBy = $derived(hasPassword ? 'password' : profile.email ? 'email' : 'confirm');
  const confirmInput = $derived(
    {
      password: { type: 'password', placeholder: 'Your password', label: 'Password to confirm' },
      email: { type: 'email', placeholder: `Type ${profile.email}`, label: 'Email to confirm' },
      confirm: { type: 'text', placeholder: 'Type DELETE', label: 'Type DELETE to confirm' }
    }[confirmBy]
  );

  let currentPassword = $state('');
  let newPassword = $state('');
  let repeatPassword = $state('');
  let changing = $state(false);

  let confirmingDelete = $state(false);
  let confirmation = $state('');
  let deleting = $state(false);
  let deleteError = $state('');

  // Job notification emails need SMTP on the backend and an address to send to.
  const canNotify = $derived(publicConfig.jobNotifications && Boolean(profile.email));
  let notifyJobEmails = $derived(profile.notify_job_emails);

  async function setNotifyJobEmails(on: boolean) {
    notifyJobEmails = on;
    try {
      await updateAccountSettings({ requestBody: { notify_job_emails: on } });
      notify.positive(on ? "You'll get an email when your jobs end" : 'Job emails switched off');
    } catch (error) {
      notifyJobEmails = !on;
      notify.apiError(error);
    }
  }

  const mismatch = $derived(repeatPassword !== '' && newPassword !== repeatPassword);

  async function submitPasswordChange() {
    changing = true;
    try {
      await changePassword({
        requestBody: { current_password: currentPassword, new_password: newPassword }
      });
      notify.positive('Password changed');
      currentPassword = newPassword = repeatPassword = '';
    } catch (error) {
      notify.apiError(error);
    } finally {
      changing = false;
    }
  }

  async function submitDelete() {
    deleting = true;
    deleteError = '';
    try {
      await deleteAccount({
        requestBody: { [confirmBy]: confirmation }
      });
      authStore.logout();
    } catch (error) {
      deleteError =
        (error as { body?: { detail?: string } })?.body?.detail ?? 'Could not delete the account.';
      deleting = false;
    }
  }
</script>

<section class="border-border mt-4 border-t pt-3">
  <h3 class="text-muted-foreground mb-2 text-xs font-semibold tracking-wide uppercase">Account</h3>

  {#if canNotify}
    <div class="mb-3">
      <Toggle
        checked={notifyJobEmails}
        onCheckedChange={setNotifyJobEmails}
        label="Email me when my jobs end"
      />
      <p class="text-muted-foreground mt-1 text-xs">
        When a run finishes, fails or is stopped — not when you cancel it yourself.
      </p>
    </div>
  {/if}

  {#if hasPassword}
    <form
      class="flex flex-col gap-2"
      onsubmit={(e) => {
        e.preventDefault();
        submitPasswordChange();
      }}
    >
      <Input
        type="password"
        bind:value={currentPassword}
        placeholder="Current password"
        aria-label="Current password"
        autocomplete="current-password"
        required
      />
      <Input
        type="password"
        bind:value={newPassword}
        placeholder="New password (at least 8 characters)"
        aria-label="New password"
        autocomplete="new-password"
        minlength={8}
        required
      />
      <Input
        type="password"
        bind:value={repeatPassword}
        placeholder="Repeat new password"
        aria-label="Repeat new password"
        autocomplete="new-password"
        required
      />
      {#if mismatch}
        <p class="text-destructive text-xs">The new passwords don't match.</p>
      {/if}
      <div class="flex justify-end">
        <Button
          type="submit"
          size="sm"
          disabled={changing || mismatch || !currentPassword || newPassword.length < 8}
        >
          Change password
        </Button>
      </div>
    </form>
  {/if}

  <div class="mt-3">
    {#if !confirmingDelete}
      <Button
        size="sm"
        variant="outline"
        class="text-destructive"
        onclick={() => (confirmingDelete = true)}
      >
        Delete account…
      </Button>
    {:else}
      <form
        class="border-destructive/40 bg-destructive/5 flex flex-col gap-2 rounded-md border p-3 text-sm"
        onsubmit={(e) => {
          e.preventDefault();
          submitDelete();
        }}
      >
        <p>
          This permanently deletes your account and everything you own: jobs and results, simulation
          files, model configs and materials (also ones you shared), projects you created and your
          API keys. It can't be undone.
        </p>
        <Input
          type={confirmInput.type}
          bind:value={confirmation}
          placeholder={confirmInput.placeholder}
          aria-label={confirmInput.label}
          autocomplete={hasPassword ? 'current-password' : 'off'}
          required
        />
        {#if deleteError}
          <p class="text-destructive text-xs">{deleteError}</p>
        {/if}
        <div class="flex justify-end gap-2">
          <Button
            size="sm"
            variant="ghost"
            onclick={() => {
              confirmingDelete = false;
              confirmation = deleteError = '';
            }}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            variant="destructive"
            disabled={deleting || !confirmation}
          >
            {deleting ? 'Deleting…' : 'Delete my account'}
          </Button>
        </div>
      </form>
    {/if}
  </div>
</section>
