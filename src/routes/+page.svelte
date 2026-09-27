<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { goto } from '$app/navigation';
  import { ArrowUpRight } from 'lucide-svelte';
  import SpecimenHero from '$lib/components/SpecimenHero.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { refreshModelFromBackend } from '$lib/utils/modelSync';

  const GUIDE = 'https://perihub.github.io/PeriHub/';

  // Built-in models (backend/app/models), each drawn as a line sketch of its
  // test specimen in a 100x50 viewBox.
  const models = [
    {
      file: 'Dogbone',
      title: 'Dogbone',
      note: 'Tensile test',
      d: 'M4 8h26c8 0 10 12 18 12h4c8 0 10-12 18-12h26v34H70c-8 0-10-12-18-12h-4c-8 0-10 12-18 12H4z'
    },
    {
      file: 'CompactTension',
      title: 'Compact Tension',
      note: 'Mode I fracture',
      // Pin holes centred in each arm: x = 0.25·L as in CompactTension.py, two half-arcs per circle.
      d: 'M24 4h52v42H24zM24 25h26M30 14.5a4 4 0 0 0 8 0a4 4 0 0 0-8 0M30 35.5a4 4 0 0 0 8 0a4 4 0 0 0-8 0'
    },
    {
      file: 'Kalthoff-Winkler',
      title: 'Kalthoff–Winkler',
      note: 'Impact-driven cracks',
      d: 'M22 4h56v42H22zM22 18h20M22 32h20M4 25h14M13 21l5 4-5 4'
    },
    {
      file: 'DCBmodel',
      title: 'DCB',
      note: 'Mode I delamination',
      d: 'M6 19h88v12H6zM6 25h34M10 19v-9M10 31v9M7 13l3-3 3 3M7 37l3 3 3-3'
    },
    {
      file: 'ENFmodel',
      title: 'ENF',
      note: 'Mode II delamination',
      d: 'M6 19h88v12H6zM6 25h30M50 5v10M47 12l3 3 3-3M12 31l-4 7h8zM88 31l-4 7h8z'
    }
  ];

  const steps = [
    ['Pick a model', 'Start from a built-in specimen or upload your own mesh.'],
    [
      'Set material & boundary conditions',
      'Choose material laws, damage models and loads per block.'
    ],
    ['Run on PeriLab', 'The input deck is written for you and solved by PeriLab.jl.'],
    ['Analyse the crack', 'Inspect damage fields, crack paths and energy release in the browser.']
  ];

  const links = [
    {
      group: 'Learn',
      items: [
        { label: 'Guide', href: GUIDE },
        { label: 'Publications', href: '/publications' },
        { label: 'Videos on YouTube', href: 'https://www.youtube.com/@PeriHub' }
      ]
    },
    {
      group: 'Build',
      items: [
        { label: 'API docs', href: '/api/docs' },
        { label: 'Source on GitHub', href: 'https://github.com/PeriHub/PeriHub' },
        { label: 'Tools', href: '/tools' }
      ]
    },
    {
      group: 'Results',
      items: [{ label: 'PeriLab results', href: 'https://perilab-results.nimbus-extern.dlr.de' }]
    }
  ];

  const external = (href: string) => href.startsWith('http');

  function openModel(m: { file: string; title: string }) {
    modelStore.selectedModel = { title: m.title, file: m.file };
    localStorage.setItem('selectedModel', JSON.stringify(modelStore.selectedModel));
    modelStore.modelData.model.ownModel = false;
    refreshModelFromBackend(m.file);
    goto('/perihub');
  }
</script>

<svelte:head>
  <title>PeriHub — peridynamic fracture simulation</title>
</svelte:head>

<div class="dark:bg-background dark:text-foreground bg-[#E8EDEE] text-[#10191D]">
  <section
    class="mx-auto grid max-w-6xl items-center gap-10 px-6 pt-14 pb-16 sm:pt-20 lg:grid-cols-[1fr_26rem]"
  >
    <div>
      <h1
        class="font-display text-5xl leading-[0.95] font-extrabold tracking-tight sm:text-7xl"
        style="font-stretch: 125%"
      >
        Peridynamics,<br />in your browser.
      </h1>
      <p class="dark:text-muted-foreground mt-6 max-w-xl text-lg text-balance text-[#10191D]/75">
        Build a model, run it on PeriLab and explore the results, all in one place. Simulate
        fracture and damage, heat transfer, thermo-mechanics or additive manufacturing processes,
        with static or dynamic solvers and your own material models.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <a
          href="/perihub"
          class="rounded-lg bg-[#00658B] px-5 py-3 font-medium text-white transition-colors hover:bg-[#0B3A4A] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B]"
        >
          Open the editor
        </a>
        <a
          href={GUIDE}
          class="dark:border-border rounded-lg border border-[#10191D]/25 px-5 py-3 font-medium transition-colors hover:border-[#00658B] hover:text-[#00658B] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B]"
        >
          Read the guide
        </a>
      </div>
    </div>

    <SpecimenHero />
  </section>

  <section class="mx-auto max-w-6xl px-6 pb-16" aria-labelledby="models-heading">
    <h2 id="models-heading" class="font-mono text-xs tracking-widest uppercase opacity-60">
      Models
    </h2>
    <ul
      class="dark:bg-border mt-4 grid grid-cols-2 gap-px overflow-hidden rounded-xl bg-[#10191D]/10 sm:grid-cols-3 lg:grid-cols-6"
    >
      {#each models as m (m.file)}
        <li>
          <button
            type="button"
            onclick={() => openModel(m)}
            class="group dark:bg-background dark:hover:bg-card flex h-full w-full flex-col bg-[#E8EDEE] p-4 text-left transition-colors hover:bg-white focus-visible:relative focus-visible:outline-2 focus-visible:outline-[#00658B]"
          >
            <svg
              viewBox="0 0 100 50"
              class="dark:text-primary w-full text-[#00658B] transition-colors group-hover:text-[#D2AE3D]"
              aria-hidden="true"
            >
              <path
                d={m.d}
                fill="none"
                stroke="currentColor"
                stroke-width="1.6"
                stroke-linejoin="round"
              />
            </svg>
            <span class="mt-3 font-medium">{m.title}</span>
            <span class="font-mono text-xs opacity-60">{m.note}</span>
          </button>
        </li>
      {/each}
      <li>
        <a
          href="/models"
          class="group dark:bg-background dark:hover:bg-card flex h-full w-full flex-col bg-[#E8EDEE] p-4 text-left transition-colors hover:bg-white focus-visible:relative focus-visible:outline-2 focus-visible:outline-[#00658B]"
        >
          <svg
            viewBox="0 0 100 50"
            class="dark:text-primary w-full text-[#00658B] transition-colors group-hover:text-[#D2AE3D]"
            aria-hidden="true"
          >
            <g fill="none" stroke="currentColor" stroke-width="1.6">
              <path d="M14 6h72v38H14z" stroke-dasharray="4 3" />
              <path d="M50 16v18M41 25h18" />
            </g>
          </svg>
          <span class="mt-3 font-medium">Own model</span>
          <span class="font-mono text-xs opacity-60">Your own geometry</span>
        </a>
      </li>
    </ul>
  </section>

  <section class="bg-[#0B3A4A] text-[#E8EDEE]" aria-labelledby="workflow-heading">
    <div class="mx-auto max-w-6xl px-6 py-14">
      <h2 id="workflow-heading" class="font-mono text-xs tracking-widest text-[#D2AE3D] uppercase">
        From specimen to crack path
      </h2>
      <ol class="mt-6 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {#each steps as [title, text], i (title)}
          <li class="border-t border-white/20 pt-4">
            <span class="font-mono text-sm text-[#D2AE3D]">{i + 1}</span>
            <h3 class="mt-1 text-lg font-semibold">{title}</h3>
            <p class="mt-2 text-sm text-white/70">{text}</p>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <section class="mx-auto grid max-w-6xl gap-10 px-6 py-14 sm:grid-cols-3">
    {#each links as { group, items } (group)}
      <div>
        <h2 class="font-mono text-xs tracking-widest uppercase opacity-60">{group}</h2>
        <ul class="mt-3 space-y-2">
          {#each items as item (item.href)}
            <li>
              <a
                href={item.href}
                target={external(item.href) ? '_blank' : undefined}
                rel={external(item.href) ? 'noopener noreferrer' : undefined}
                class="inline-flex items-center gap-1 text-lg font-medium underline decoration-[#00658B]/30 underline-offset-4 hover:decoration-[#00658B] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B]"
              >
                {item.label}
                {#if external(item.href)}<ArrowUpRight
                    class="size-4 opacity-60"
                    aria-hidden="true"
                  />{/if}
              </a>
            </li>
          {/each}
        </ul>
      </div>
    {/each}
  </section>
</div>
