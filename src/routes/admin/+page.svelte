<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Tabs } from 'bits-ui';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import UsersTab from '$lib/components/admin/UsersTab.svelte';
  import JobsTab from '$lib/components/admin/JobsTab.svelte';
  import SettingsTab from '$lib/components/admin/SettingsTab.svelte';
  import HousekeepingTab from '$lib/components/admin/HousekeepingTab.svelte';

  const tabClass =
    'px-3 py-2 pr-4 font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground';
</script>

<svelte:head>
  <title>Admin — PeriHub</title>
</svelte:head>

<div class="bg-background text-foreground">
  <div class="mx-auto max-w-6xl px-6 pt-12 pb-20 sm:pt-16">
    <h1
      class="font-display text-3xl leading-none font-extrabold tracking-tight sm:text-4xl"
      style="font-stretch: 125%"
    >
      Admin
    </h1>

    {#if authStore.role !== 'admin'}
      <p class="text-muted-foreground mt-3">This page is only available to admins.</p>
    {:else}
      <Tabs.Root value="users" class="mt-8">
        <Tabs.List class="border-border flex flex-wrap gap-x-6 border-b">
          <Tabs.Trigger value="users" class={tabClass}>Users</Tabs.Trigger>
          <Tabs.Trigger value="jobs" class={tabClass}>Jobs & usage</Tabs.Trigger>
          <Tabs.Trigger value="settings" class={tabClass}>Settings</Tabs.Trigger>
          <Tabs.Trigger value="housekeeping" class={tabClass}>Housekeeping</Tabs.Trigger>
        </Tabs.List>
        <div class="pt-6">
          <Tabs.Content value="users"><UsersTab /></Tabs.Content>
          <Tabs.Content value="jobs"><JobsTab /></Tabs.Content>
          <Tabs.Content value="settings"><SettingsTab /></Tabs.Content>
          <Tabs.Content value="housekeeping"><HousekeepingTab /></Tabs.Content>
        </div>
      </Tabs.Root>
    {/if}
  </div>
</div>
