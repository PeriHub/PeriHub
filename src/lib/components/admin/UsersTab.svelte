<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { adminListUsers, adminUpdateUser } from '$lib/client';
  import type { AdminUser, AdminUserUpdate } from '$lib/client';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import { notify } from '$lib/utils/notify';

  let users = $state<AdminUser[]>([]);

  async function load() {
    users = await adminListUsers().catch((e) => {
      notify.apiError(e);
      return [];
    });
  }

  async function update(user: AdminUser, change: AdminUserUpdate) {
    try {
      Object.assign(user, await adminUpdateUser({ userId: user.id, requestBody: change }));
    } catch (e) {
      notify.apiError(e); // e.g. 409 "at least one active admin must remain"
      await load(); // revert the row
    }
  }

  const when = (date: string | null) => (date ? new Date(date).toLocaleString() : '—');

  onMount(load);
</script>

<div class="overflow-x-auto">
  <table class="w-full text-left text-sm">
    <thead class="text-muted-foreground border-border border-b">
      <tr>
        <th class="py-2 pr-4 font-medium">Name</th>
        <th class="py-2 pr-4 font-medium">Email</th>
        <th class="py-2 pr-4 font-medium">Login</th>
        <th class="py-2 pr-4 font-medium">Role</th>
        <th class="py-2 pr-4 font-medium">Active</th>
        <th class="py-2 pr-4 font-medium">Last login</th>
        <th class="py-2 pr-4 text-right font-medium">Jobs</th>
      </tr>
    </thead>
    <!-- Re-render rows on reload so controls snap back after a rejected change. -->
    {#key users}
      <tbody>
        {#each users as user (user.id)}
          <tr class="border-border border-b last:border-0">
            <td class="py-2 pr-4">{user.display_name}</td>
            <td class="py-2 pr-4">{user.email ?? '—'}</td>
            <td class="py-2 pr-4">{user.auth_provider}</td>
            <td class="py-2 pr-4">
              <Select
                value={user.role}
                aria-label="Role of {user.display_name}"
                onchange={(e) =>
                  update(user, {
                    role: e.currentTarget.value as AdminUserUpdate['role']
                  })}
              >
                <option value="admin">admin</option>
                <option value="developer">developer</option>
                <option value="member">member</option>
                <option value="viewer">viewer</option>
              </Select>
            </td>
            <td class="py-2 pr-4">
              <Toggle
                checked={user.is_active}
                ariaLabel="{user.display_name} active"
                onCheckedChange={(active) => update(user, { is_active: active })}
              />
            </td>
            <td class="py-2 pr-4">{when(user.last_login_at)}</td>
            <td class="py-2 pr-4 text-right">{user.job_count}</td>
          </tr>
        {:else}
          <tr><td colspan="7" class="text-muted-foreground py-4">No users.</td></tr>
        {/each}
      </tbody>
    {/key}
  </table>
</div>
