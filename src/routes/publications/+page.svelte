<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { ArrowUpRight } from 'lucide-svelte';
  // @ts-expect-error no types shipped
  import bibtexParse from 'bibtex-parse-js';
  import { getPublications } from '$lib/client';
  import { notify } from '$lib/utils/notify';

  interface BibEntry {
    entryType: string;
    entryTags: Record<string, string>;
  }

  interface Publication {
    title: string;
    url?: string;
    doi?: string;
    authors: string;
    venue?: string;
    year: string;
    type: string;
  }

  const typeLabels: Record<string, string> = {
    article: 'Article',
    conference: 'Conference paper',
    inproceedings: 'Conference paper',
    software: 'Software',
    dataset: 'Dataset',
    techreport: 'Report'
  };

  let publications = $state<Publication[]>([]);
  let loaded = $state(false);

  const years = $derived([...new Set(publications.map((p) => p.year))]);

  function latexToUtf(input: string) {
    return input.replace(/{\\"a}/gi, 'ä');
  }

  // The .bib mixes "Last, First" and "First Last"; show everyone as "First Last".
  const formatAuthors = (authors: string) =>
    authors
      .split(/\s+and\s+/)
      .map((a) =>
        a
          .split(',')
          .map((s) => s.trim())
          .reverse()
          .join(' ')
      )
      .join(', ');

  function toPublication(entry: BibEntry): Publication {
    const tags = Object.fromEntries(
      Object.entries(entry.entryTags).map(([k, v]) => [k.toLowerCase(), v])
    );
    return {
      title: tags.title ?? 'Untitled',
      url: tags.url,
      doi: tags.doi?.replace(/^https?:\/\/(dx\.)?doi\.org\//, ''),
      authors: formatAuthors(tags.author ?? ''),
      venue: tags.journal ?? tags.booktitle ?? tags.publisher ?? tags.institution,
      year: tags.year ?? 'Undated',
      type: typeLabels[entry.entryType.toLowerCase()] ?? 'Other'
    };
  }

  onMount(async () => {
    try {
      const response = await getPublications();
      const entries: BibEntry[] = bibtexParse.toJSON(latexToUtf(response as unknown as string));
      publications = entries.map(toPublication).sort((a, b) => b.year.localeCompare(a.year));
    } catch (error) {
      notify.apiError(error);
    } finally {
      loaded = true;
    }
  });
</script>

<svelte:head>
  <title>Publications — PeriHub</title>
</svelte:head>

<div class="bg-background text-foreground">
  <div class="mx-auto max-w-6xl px-6 pt-12 pb-20 sm:pt-16">
    <header class="max-w-2xl">
      <h1
        class="font-display text-3xl leading-none font-extrabold tracking-tight sm:text-4xl"
        style="font-stretch: 125%"
      >
        Publications
      </h1>
      <p class="text-muted-foreground mt-3 text-balance">
        Papers, software releases and datasets behind PeriHub and PeriLab.
      </p>
    </header>

    {#if loaded && publications.length === 0}
      <p class="text-muted-foreground mt-10">
        The publication list couldn't be loaded. Reload the page to try again.
      </p>
    {:else}
      <div class="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[14rem_minmax(0,1fr)]">
        <nav aria-label="Years" class="lg:sticky lg:top-6 lg:self-start">
          <ul
            class="border-border flex flex-wrap gap-x-5 gap-y-2 border-b pb-3 lg:flex-col lg:flex-nowrap lg:border-b-0 lg:border-l lg:pb-0"
          >
            {#each years as year (year)}
              <li class="shrink-0">
                <a
                  href="#year-{year}"
                  class="hover:text-primary lg:hover:border-primary block font-mono text-sm focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B] lg:-ml-px lg:border-l-2 lg:border-transparent lg:pl-4"
                >
                  {year}
                  <span class="text-muted-foreground text-xs">
                    · {publications.filter((p) => p.year === year).length}
                  </span>
                </a>
              </li>
            {/each}
          </ul>
        </nav>

        <div>
          {#each years as year (year)}
            <section
              id="year-{year}"
              aria-labelledby="year-{year}-heading"
              class="border-border scroll-mt-6 border-t py-6 first:border-t-0 first:pt-0"
            >
              <h2 id="year-{year}-heading" class="text-primary font-mono text-sm tracking-wide">
                {year}
              </h2>
              <ul class="divide-border mt-2 divide-y">
                {#each publications.filter((p) => p.year === year) as p (p.url ?? p.title)}
                  <li class="max-w-3xl py-4">
                    <p class="text-muted-foreground font-mono text-xs">{p.type}</p>
                    <h3 class="mt-1 font-semibold">
                      {#if p.url}
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          class="decoration-primary/30 hover:decoration-primary underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B]"
                        >
                          {p.title}<ArrowUpRight
                            class="ml-0.5 inline size-3.5 align-baseline opacity-60"
                            aria-hidden="true"
                          />
                        </a>
                      {:else}
                        {p.title}
                      {/if}
                    </h3>
                    <p class="text-muted-foreground mt-1 text-sm">{p.authors}</p>
                    {#if p.venue || p.doi}
                      <p class="mt-1 text-sm">
                        {#if p.venue}<em>{p.venue}</em>{/if}
                        {#if p.doi}
                          <span class="text-muted-foreground ml-1 font-mono text-xs"
                            >doi:{p.doi}</span
                          >
                        {/if}
                      </p>
                    {/if}
                  </li>
                {/each}
              </ul>
            </section>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>
