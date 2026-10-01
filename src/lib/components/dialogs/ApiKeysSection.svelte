<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Copy, Trash2 } from 'lucide-svelte';
  import { createApiKey, listApiKeys, revokeApiKey } from '$lib/client';
  import type { ApiKeyInfo } from '$lib/client';
  import { notify } from '$lib/utils/notify';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';

  let keys = $state<ApiKeyInfo[]>([]);
  let name = $state('');
  let newKey = $state<string | null>(null);
  let busy = $state(false);

  async function load() {
    try {
      keys = await listApiKeys();
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function create() {
    busy = true;
    try {
      const created = await createApiKey({ requestBody: { name: name.trim() } });
      newKey = created.key;
      name = '';
      await load();
    } catch (error) {
      notify.apiError(error);
    } finally {
      busy = false;
    }
  }

  async function revoke(key: ApiKeyInfo) {
    if (!confirm(`Revoke "${key.name}"? Scripts using it will stop working.`)) return;
    try {
      await revokeApiKey({ keyId: key.id });
      await load();
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function copy() {
    if (!newKey) return;
    try {
      await navigator.clipboard.writeText(newKey);
      notify.positive('API key copied');
    } catch (error) {
      notify.apiError(error);
    }
  }

  const date = (value?: string | null) => (value ? new Date(value).toLocaleDateString() : '—');

  load();
</script>

<section class="border-border mt-4 border-t pt-3">
  <h3 class="text-muted-foreground mb-2 text-xs font-semibold tracking-wide uppercase">API keys</h3>

  {#if newKey}
    <div class="bg-warning/20 mb-3 rounded-md px-3 py-2 text-sm">
      <p class="mb-1">Copy your new key now — it won't be shown again.</p>
      <div class="flex items-center gap-2">
        <code class="bg-muted min-w-0 flex-1 truncate rounded px-2 py-1 text-xs">{newKey}</code>
        <Button size="sm" variant="outline" onclick={copy} aria-label="Copy API key">
          <Copy class="h-4 w-4" />
        </Button>
      </div>
    </div>
  {/if}

  {#if keys.length}
    <ul class="mb-3 space-y-1.5 text-sm">
      {#each keys as key (key.id)}
        <li class="flex items-center justify-between gap-2">
          <div class="min-w-0">
            <span class="font-medium">{key.name}</span>
            <code class="text-muted-foreground ml-1 text-xs">{key.prefix}…</code>
            <div class="text-muted-foreground text-xs">
              Created {date(key.created_at)} · Last used {date(key.last_used_at)}
            </div>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onclick={() => revoke(key)}
            aria-label={`Revoke ${key.name}`}
          >
            <Trash2 class="h-4 w-4" />
          </Button>
        </li>
      {/each}
    </ul>
  {/if}

  <form
    class="flex gap-2"
    onsubmit={(e) => {
      e.preventDefault();
      create();
    }}
  >
    <Input
      bind:value={name}
      placeholder="Key name, e.g. CI"
      maxlength={100}
      aria-label="API key name"
    />
    <Button type="submit" size="sm" disabled={!name.trim() || busy}>Create</Button>
  </form>
  <p class="text-muted-foreground mt-1 text-xs">
    Send as the <code>X-Api-Key</code> header. A key has the same access as your account.
  </p>
</section>
