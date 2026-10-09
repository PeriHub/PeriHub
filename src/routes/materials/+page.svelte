<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Dialog } from 'bits-ui';
  import { Plus, Trash2 } from 'lucide-svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { notify } from '$lib/utils/notify';
  import {
    createLibraryItem,
    deleteLibraryItem,
    listLibraryItems,
    listTeams,
    updateLibraryItem
  } from '$lib/client';
  import type { LibraryItemIn, LibraryItemOut, Material, TeamOut } from '$lib/client';
  import { VISIBILITY_LABELS, newMaterial, toLibraryProperties } from '$lib/utils/material-library';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import MaterialEditor from '$lib/components/MaterialEditor.svelte';

  let items = $state<LibraryItemOut[]>([]);
  let teams = $state<TeamOut[]>([]);
  let loaded = $state(false);
  let search = $state('');

  // The open material: an existing library item, or a new one (selected = null, creating = true).
  let selected = $state<LibraryItemOut | null>(null);
  let creating = $state(false);
  let draft = $state<Material | null>(null);
  let visibility = $state<NonNullable<LibraryItemIn['visibility']>>('private');
  let teamId = $state<string | null>(null);
  let dialogDelete = $state(false);

  const filtered = $derived(
    items.filter((i) => i.name.toLowerCase().includes(search.trim().toLowerCase()))
  );
  const editable = $derived(creating || !!selected?.can_edit);

  async function fetchItems() {
    try {
      items = await listLibraryItems({ kind: 'material' });
    } catch (error) {
      notify.apiError(error);
    }
    loaded = true;
  }

  function open(item: LibraryItemOut) {
    selected = item;
    creating = false;
    // Snapshot, not structuredClone: list items are $state proxies, which can't be cloned.
    draft = { ...$state.snapshot(item.properties ?? {}), name: item.name } as Material;
    visibility = item.visibility as typeof visibility;
    teamId = item.team_id ?? null;
  }

  function startNew() {
    selected = null;
    creating = true;
    draft = newMaterial();
    visibility = 'private';
    teamId = null;
  }

  async function save() {
    if (!draft) return;
    const material = $state.snapshot(draft) as Material;
    const requestBody: LibraryItemIn = {
      name: material.name,
      visibility,
      team_id: visibility === 'team' ? teamId : null,
      project_id: selected?.project_id ?? null,
      tags: selected?.tags ?? [],
      source: selected?.source ?? null,
      properties: toLibraryProperties(material)
    };
    try {
      const saved = selected
        ? await updateLibraryItem({ kind: 'material', itemId: selected.id, requestBody })
        : await createLibraryItem({ kind: 'material', requestBody });
      notify.positive(`Saved ${saved.name}`);
      await fetchItems();
      open(items.find((i) => i.id === saved.id) ?? saved);
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function confirmDelete() {
    dialogDelete = false;
    if (!selected) return;
    try {
      await deleteLibraryItem({ kind: 'material', itemId: selected.id });
      notify.positive(`Deleted ${selected.name}`);
      selected = null;
      draft = null;
    } catch (error) {
      notify.apiError(error);
    }
    await fetchItems();
  }

  onMount(async () => {
    if (authStore.isGuest) return;
    await fetchItems();
    // Only needed for "team" sharing; an instance without teams just doesn't offer it.
    teams = await listTeams().catch(() => []);
  });
</script>

<svelte:head>
  <title>Materials — PeriHub</title>
</svelte:head>

<div class="bg-background text-foreground">
  <div class="mx-auto max-w-[110rem] px-6 pt-12 pb-20 sm:pt-16">
    <header class="max-w-2xl">
      <h1
        class="font-display text-3xl leading-none font-extrabold tracking-tight sm:text-4xl"
        style="font-stretch: 125%"
      >
        Materials
      </h1>
      <p class="text-muted-foreground mt-3 text-balance">
        Your material library. Materials are private until you share them with a team, your
        organization or everyone, and can be loaded into a model in the editor's Material section.
      </p>
    </header>

    {#if authStore.isGuest}
      <p class="border-border mt-10 max-w-md rounded-xl border border-dashed p-6 text-sm">
        The material library needs an account - sign up or log in to create and share materials.
      </p>
    {:else}
      <div class="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[16rem_minmax(0,1fr)]">
        <nav aria-label="Materials" class="space-y-4 lg:sticky lg:top-6 lg:self-start">
          <Button variant="outline" class="w-full" onclick={startNew}>
            <Plus /> New material
          </Button>
          <Input
            type="search"
            placeholder="Search materials"
            aria-label="Search materials"
            bind:value={search}
          />
          {#if loaded && items.length === 0}
            <p class="text-muted-foreground text-sm">No materials yet.</p>
          {/if}
          <ul
            class="border-border flex gap-x-6 gap-y-3 overflow-x-auto border-b pb-3 lg:flex-col lg:border-b-0 lg:border-l lg:pb-0"
          >
            {#each filtered as m (m.id)}
              <li class="shrink-0">
                <button
                  type="button"
                  aria-current={selected?.id === m.id ? 'true' : undefined}
                  onclick={() => open(m)}
                  class="group block text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B] lg:-ml-px lg:border-l-2 lg:pl-4 {selected?.id ===
                  m.id
                    ? 'border-primary text-primary'
                    : 'hover:border-primary border-transparent'}"
                >
                  <span class="group-hover:text-primary font-medium">{m.name}</span>
                  <span class="text-muted-foreground block text-xs">
                    {VISIBILITY_LABELS[m.visibility] ?? m.visibility}
                    {#if !m.can_edit || m.visibility === 'private'}· {m.owner_name}{/if}
                  </span>
                </button>
              </li>
            {/each}
          </ul>
        </nav>

        {#if draft}
          <section aria-labelledby="material-heading" class="min-w-0">
            <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
              <div class="min-w-0">
                <h2 id="material-heading" class="text-2xl font-semibold tracking-tight">
                  {creating ? 'New material' : selected?.name}
                </h2>
                {#if selected}
                  <p class="text-muted-foreground mt-1 text-sm">
                    Owner: {selected.owner_name}{editable ? '' : ' · read only'}
                  </p>
                {/if}
              </div>
              <div class="flex gap-2">
                {#if selected?.can_edit}
                  <Button
                    variant="ghost"
                    class="text-destructive hover:text-destructive"
                    onclick={() => (dialogDelete = true)}
                  >
                    <Trash2 /> Delete
                  </Button>
                {/if}
                {#if editable}
                  <Button onclick={save}>{creating ? 'Create' : 'Save'}</Button>
                {/if}
              </div>
            </div>

            <!-- Native disabled fieldset: everything inside is read only for materials you can't edit. -->
            <fieldset disabled={!editable} class="mt-6 space-y-6">
              <div class="flex flex-wrap items-end gap-3">
                <div class="space-y-1">
                  <Label for="mat-visibility">Sharing</Label>
                  <Select id="mat-visibility" class="w-48" bind:value={visibility}>
                    {#each Object.entries(VISIBILITY_LABELS) as [value, label] (value)}
                      <option {value} disabled={value === 'team' && teams.length === 0}
                        >{label}</option
                      >
                    {/each}
                  </Select>
                </div>
                {#if visibility === 'team'}
                  <div class="space-y-1">
                    <Label for="mat-team">Team</Label>
                    <Select id="mat-team" class="w-56" bind:value={teamId}>
                      {#each teams as team (team.id)}
                        <option value={team.id}>{team.name}</option>
                      {/each}
                    </Select>
                  </div>
                {/if}
              </div>

              <div class="border-border space-y-3 rounded-md border p-4">
                <MaterialEditor bind:material={draft} idPrefix="lib-mat" />
              </div>
            </fieldset>
          </section>
        {:else if loaded && items.length > 0}
          <p class="text-muted-foreground">Select a material, or create a new one.</p>
        {/if}
      </div>
    {/if}
  </div>
</div>

<Dialog.Root bind:open={dialogDelete}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="text-lg font-semibold">Delete {selected?.name}?</Dialog.Title>
      <Dialog.Description class="text-muted-foreground mt-1 text-sm">
        It is removed from the library for everyone it is shared with. Models that already loaded it
        keep their copy. This can't be undone.
      </Dialog.Description>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogDelete = false)}>Cancel</Button>
        <Button variant="destructive" onclick={confirmDelete}>Delete material</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
