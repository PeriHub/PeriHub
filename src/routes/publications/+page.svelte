<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  // @ts-expect-error no types shipped
  import bibtexParse from 'bibtex-parse-js';
  import { getPublications } from '$lib/client';
  import { notify } from '$lib/utils/notify';
  import Card from '$lib/components/ui/Card.svelte';

  interface BibEntry {
    entryTags: Record<string, string>;
  }

  let entries = $state<BibEntry[]>([]);

  function latexToUtf(input: string) {
    return input.replace(/{\\"a}/gi, 'ä');
  }

  function field(entry: BibEntry, ...keys: string[]) {
    for (const key of keys) {
      if (entry.entryTags[key]) return entry.entryTags[key];
    }
    return undefined;
  }

  onMount(async () => {
    try {
      const response = await getPublications();
      const bibData = latexToUtf(response as unknown as string);
      entries = bibtexParse.toJSON(bibData);
    } catch (error) {
      notify.apiError(error);
    }
  });
</script>

<svelte:head>
  <title>Publications — PeriHub</title>
</svelte:head>

<div class="mx-auto max-w-3xl space-y-4 px-6 py-10">
  <h1 class="text-2xl font-semibold tracking-tight">Publications</h1>

  {#each entries as entry (field(entry, 'URL', 'url', 'Title', 'title'))}
    {@const title = field(entry, 'Title', 'title')}
    {@const url = field(entry, 'URL', 'url')}
    {@const author = field(entry, 'Author', 'author')}
    {@const journal = field(entry, 'Journal', 'journal')}
    {@const month = field(entry, 'Month', 'month')}
    {@const year = field(entry, 'Year', 'year')}

    <Card class="p-4">
      {#if title}
        {#if url}
          <a href={url} class="font-medium text-primary hover:underline">{title}</a>
        {:else}
          <span class="font-medium">{title}</span>
        {/if}
      {/if}
      {#if author}
        <div class="mt-1 text-sm text-muted-foreground">{author}</div>
      {/if}
      <div class="mt-1 text-sm">
        {#if journal}<em>{journal}</em>&nbsp;{/if}
        {#if month}{month},&nbsp;{/if}
        {#if year}{year}{/if}.
      </div>
    </Card>
  {:else}
    <p class="text-muted-foreground">No publications found.</p>
  {/each}
</div>
