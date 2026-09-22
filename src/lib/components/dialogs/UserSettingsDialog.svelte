<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { Lock, X } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { getVersion, getSettings, updateSettings } from '$lib/client';
  import type { VersionData, SettingInfo } from '$lib/client';
  import { ApiError } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Label from '$lib/components/ui/Label.svelte';

  let { open = $bindable(false) }: { open?: boolean } = $props();

  let version = $state<Partial<VersionData>>({});

  // Server-side env-var configuration (support/globals.py), see
  // routers/settings.py. `settings` always reflects the backend's current
  // state; `edited` holds only the keys the person has actually changed in
  // this dialog, keyed the same way, so a save only ever sends a diff.
  let settings = $state<SettingInfo[]>([]);
  let edited = $state<Record<string, string>>({});
  let settingsLoading = $state(true);
  let settingsError = $state<string | null>(null);
  let saving = $state(false);
  let saveNote = $state<string | null>(null);

  onMount(async () => {
    try {
      version = await getVersion();
    } catch (error) {
      console.error(error);
    }
    await loadSettings();
  });

  async function loadSettings() {
    settingsLoading = true;
    settingsError = null;
    try {
      const response = await getSettings();
      settings = response.settings;
      edited = {};
    } catch (error) {
      console.error(error);
      settingsError = 'Could not load server configuration.';
    } finally {
      settingsLoading = false;
    }
  }

  // bool fields round-trip as the literal strings globals.py's os.getenv(...)
  // comparisons expect ("True"/"False"), not JSON booleans - see
  // support/runtime_settings.py.
  function currentValue(setting: SettingInfo): string {
    return edited[setting.key] ?? setting.value;
  }

  function setValue(setting: SettingInfo, value: string) {
    if (value === setting.value) {
      delete edited[setting.key];
    } else {
      edited[setting.key] = value;
    }
  }

  function toBool(value: string): boolean {
    return value === 'True';
  }

  const hasChanges = $derived(Object.keys(edited).length > 0);

  async function save() {
    if (!hasChanges) return;
    saving = true;
    settingsError = null;
    saveNote = null;
    try {
      const response = await updateSettings({ requestBody: { values: edited } });
      settings = response.settings;
      edited = {};
      saveNote =
        response.restart_required_note ?? 'Saved. Restart the backend for this to take effect.';
    } catch (error) {
      console.error(error);
      settingsError =
        error instanceof ApiError && typeof (error.body as { detail?: string })?.detail === 'string'
          ? (error.body as { detail: string }).detail
          : 'Could not save server configuration.';
    } finally {
      saving = false;
    }
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 flex max-h-[85vh] w-[min(92vw,36rem)] -translate-x-1/2 -translate-y-1/2 flex-col rounded-xl border p-5 shadow-lg"
    >
      <div class="mb-3 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Settings</Dialog.Title>
        <Dialog.Close class="hover:bg-muted rounded-full p-1.5">
          <X class="h-4 w-4" />
        </Dialog.Close>
      </div>

      <div class="space-y-5 overflow-y-auto pr-1">
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-muted-foreground">Logged in as</dt>
            <dd class="font-medium">{defaultStore.username}</dd>
          </div>
          {#if defaultStore.trial}
            <div class="bg-warning/20 text-warning-foreground rounded-md px-3 py-2">
              Trial mode enabled — some features are disabled.
            </div>
          {/if}
          {#if defaultStore.cluster}
            <div class="flex justify-between gap-4">
              <dt class="text-muted-foreground">Configured cluster</dt>
              <dd class="font-medium">{defaultStore.cluster}</dd>
            </div>
          {/if}
          <div class="flex justify-between gap-4">
            <dt class="text-muted-foreground">PeriHub version</dt>
            <dd class="font-medium">{version.current ?? '—'} / {version.latest ?? '—'}</dd>
          </div>
          <div class="flex justify-between gap-4">
            <dt class="text-muted-foreground">PeriLab version</dt>
            <dd class="font-medium">
              {version.perilab_current ?? '—'} / {version.perilab_latest ?? '—'}
            </dd>
          </div>
        </dl>

        <div class="border-border border-t pt-4">
          <h3 class="mb-1 text-sm font-semibold">Server configuration</h3>
          <p class="text-muted-foreground mb-3 text-xs">
            From this backend's environment variables (support/globals.py). Anything already set via
            the real deployment environment is read-only here; anything else can be changed and is
            saved for next time the backend starts.
          </p>

          {#if settingsLoading}
            <p class="text-muted-foreground text-sm">Loading…</p>
          {:else if settings.length === 0}
            <p class="text-muted-foreground text-sm">No configurable settings available.</p>
          {:else}
            <div class="space-y-3">
              {#each settings as setting (setting.key)}
                <div class="flex items-start justify-between gap-4">
                  <div class="min-w-0">
                    <Label class="flex items-center gap-1.5 font-normal">
                      {setting.label}
                      {#if !setting.editable}
                        <Lock
                          class="text-muted-foreground h-3 w-3"
                          aria-label="Set via environment"
                        />
                      {/if}
                    </Label>
                    {#if setting.description}
                      <p class="text-muted-foreground text-xs">{setting.description}</p>
                    {/if}
                  </div>

                  <div class="w-44 shrink-0">
                    {#if !setting.editable}
                      <p
                        class="truncate text-right text-sm font-medium"
                        title={setting.type === 'secret' ? undefined : setting.value}
                      >
                        {#if setting.type === 'secret'}
                          {setting.is_set ? 'Configured' : 'Not set'}
                        {:else}
                          {setting.value || '—'}
                        {/if}
                      </p>
                    {:else if setting.type === 'bool'}
                      <div class="flex justify-end">
                        <Toggle
                          bind:checked={
                            () => toBool(currentValue(setting)),
                            (value) => setValue(setting, value ? 'True' : 'False')
                          }
                          id={setting.key}
                        />
                      </div>
                    {:else if setting.type === 'int'}
                      <Input
                        type="number"
                        value={currentValue(setting)}
                        oninput={(e) =>
                          setValue(setting, (e.currentTarget as HTMLInputElement).value)}
                      />
                    {:else if setting.type === 'secret'}
                      <Input
                        type="password"
                        value={edited[setting.key] ?? ''}
                        placeholder={setting.is_set ? 'Unchanged' : 'Not set'}
                        oninput={(e) =>
                          setValue(setting, (e.currentTarget as HTMLInputElement).value)}
                      />
                    {:else if setting.choices && setting.choices.length > 0}
                      <Select
                        value={currentValue(setting)}
                        onchange={(e) =>
                          setValue(setting, (e.currentTarget as HTMLSelectElement).value)}
                      >
                        {#each setting.choices as choice (choice)}
                          <option value={choice}>{choice}</option>
                        {/each}
                      </Select>
                    {:else}
                      <Input
                        type="text"
                        value={currentValue(setting)}
                        oninput={(e) =>
                          setValue(setting, (e.currentTarget as HTMLInputElement).value)}
                      />
                    {/if}
                  </div>
                </div>
              {/each}
            </div>

            {#if settingsError}
              <p class="text-destructive mt-3 text-sm">{settingsError}</p>
            {/if}
            {#if saveNote}
              <p class="bg-warning/20 text-warning-foreground mt-3 rounded-md px-3 py-2 text-xs">
                {saveNote}
              </p>
            {/if}

            <div class="mt-3 flex justify-end">
              <Button size="sm" disabled={!hasChanges || saving} onclick={save}>
                {saving ? 'Saving…' : 'Save changes'}
              </Button>
            </div>
          {/if}
        </div>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
