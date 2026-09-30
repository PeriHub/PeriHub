<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGetSettings, adminUpdateSettings } from '$lib/client';
  import type { AdminSettingsResponse } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import { notify } from '$lib/utils/notify';

  let settings = $state<AdminSettingsResponse | null>(null);

  type GuestLimitKey =
    | 'guest_max_nodes'
    | 'guest_max_output_steps'
    | 'guest_max_job_minutes'
    | 'guest_max_concurrent_jobs'
    | 'guest_retention_days';
  const guestLimitFields: [GuestLimitKey, string, string][] = [
    ['guest_max_nodes', 'Max. nodes per model', ''],
    ['guest_max_output_steps', 'Max. output steps', 'Bounds the result size.'],
    ['guest_max_job_minutes', 'Max. job duration (minutes)', 'Longer guest jobs are cancelled.'],
    ['guest_max_concurrent_jobs', 'Max. concurrent jobs per guest', ''],
    ['guest_retention_days', 'Delete guests after (days)', 'Removes the account and its data.']
  ];

  async function save() {
    if (!settings) return;
    try {
      // `overridden` rides along and is ignored by the backend.
      settings = await adminUpdateSettings({ requestBody: settings });
      notify.positive('Settings saved');
    } catch (e) {
      notify.apiError(e);
    }
  }

  onMount(async () => {
    settings = await adminGetSettings().catch((e) => {
      notify.apiError(e);
      return null;
    });
  });
</script>

{#snippet source(key: string)}
  {#if settings && !settings.overridden.includes(key)}
    <span class="text-muted-foreground text-xs font-normal">(env default)</span>
  {/if}
{/snippet}

{#if settings}
  <form
    class="grid max-w-lg gap-5"
    onsubmit={(e) => {
      e.preventDefault();
      save();
    }}
  >
    <div class="grid gap-1.5">
      <Label for="max-local"
        >Max. concurrent jobs (instance) {@render source('max_concurrent_local_jobs')}</Label
      >
      <Input id="max-local" type="number" min="1" bind:value={settings.max_concurrent_local_jobs} />
    </div>
    <div class="grid gap-1.5">
      <Label for="max-user">
        Max. concurrent jobs per user {@render source('max_concurrent_jobs_per_user')}
      </Label>
      <Input
        id="max-user"
        type="number"
        min="0"
        bind:value={settings.max_concurrent_jobs_per_user}
      />
      <p class="text-muted-foreground text-xs">0 disables the per-user limit.</p>
    </div>
    <div class="flex items-center gap-2">
      <Toggle label="Allow new signups" bind:checked={settings.signup_open} />
      {@render source('signup_open')}
    </div>
    <div class="grid gap-1.5">
      <Label for="default-role">Role for new users {@render source('default_role')}</Label>
      <Select id="default-role" bind:value={settings.default_role}>
        <option value="member">member</option>
        <option value="viewer">viewer</option>
      </Select>
    </div>
    <div class="grid gap-1.5">
      <Label for="perilab-url">External PeriLab URL {@render source('external_perilab_url')}</Label>
      <Input
        id="perilab-url"
        type="url"
        placeholder="https://perilab.example.com"
        bind:value={settings.external_perilab_url}
      />
      <p class="text-muted-foreground text-xs">Only used when SOLVER_BACKEND=external.</p>
    </div>
    <h3 class="mt-4 text-base font-semibold">Guest access</h3>
    <div class="flex items-center gap-2">
      <Toggle
        label="Let visitors use PeriHub without an account"
        bind:checked={settings.guest_access}
      />
      {@render source('guest_access')}
    </div>
    {#each guestLimitFields as [key, label, hint] (key)}
      <div class="grid gap-1.5">
        <Label for={key}>{label} {@render source(key)}</Label>
        <Input id={key} type="number" min="1" bind:value={settings[key]} />
        {#if hint}<p class="text-muted-foreground text-xs">{hint}</p>{/if}
      </div>
    {/each}
    <div>
      <Button type="submit">Save</Button>
    </div>
  </form>
{/if}
