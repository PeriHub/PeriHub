<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { adminGetAuditLog, deleteStaleUserData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import { notify } from '$lib/utils/notify';

  let days = $state(30);
  let entries = $state<Record<string, unknown>[]>([]);

  async function loadLog() {
    entries = await adminGetAuditLog({ limit: 200 }).catch((e) => {
      notify.apiError(e);
      return [];
    });
  }

  async function cleanup() {
    if (!confirm(`Delete all user simulation data older than ${days} days? This cannot be undone.`))
      return;
    try {
      const result = await deleteStaleUserData({ days });
      notify.positive(result ? String(result) : 'Nothing to delete');
    } catch (e) {
      notify.apiError(e);
    }
    await loadLog();
  }

  onMount(loadLog);
</script>

<h2 class="text-lg font-semibold">Stale user data</h2>
<div class="mt-3 flex items-end gap-3">
  <div class="grid gap-1.5">
    <Label for="stale-days">Older than (days)</Label>
    <Input id="stale-days" type="number" min="1" class="w-32" bind:value={days} />
  </div>
  <Button variant="destructive" onclick={cleanup}>Delete stale data</Button>
</div>

<h2 class="mt-10 text-lg font-semibold">Audit log</h2>
<div class="mt-3 overflow-x-auto">
  <table class="w-full text-left text-sm">
    <thead class="text-muted-foreground border-border border-b">
      <tr>
        <th class="py-2 pr-4 font-medium">Time</th>
        <th class="py-2 pr-4 font-medium">User</th>
        <th class="py-2 pr-4 font-medium">Action</th>
        <th class="py-2 pr-4 font-medium">Target</th>
        <th class="py-2 font-medium">Result</th>
      </tr>
    </thead>
    <tbody>
      {#each entries as entry, i (i)}
        <tr class="border-border border-b last:border-0">
          <td class="py-2 pr-4 whitespace-nowrap">
            {new Date(String(entry.timestamp)).toLocaleString()}
          </td>
          <td class="py-2 pr-4">{entry.username}</td>
          <td class="py-2 pr-4">{entry.action}</td>
          <td class="py-2 pr-4">{entry.target}</td>
          <td class="py-2">{entry.result}</td>
        </tr>
      {:else}
        <tr><td colspan="5" class="text-muted-foreground py-4">No entries.</td></tr>
      {/each}
    </tbody>
  </table>
</div>
