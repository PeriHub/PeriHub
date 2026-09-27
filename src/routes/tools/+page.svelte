<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import ConversionCard from '$lib/components/tools/ConversionCard.svelte';
  import SiConversionCard from '$lib/components/tools/SiConversionCard.svelte';
  import StiffnessCard from '$lib/components/tools/StiffnessCard.svelte';
  import AmplitudeCard from '$lib/components/tools/AmplitudeCard.svelte';

  // Each tool is labelled by what goes in and what comes out; the index repeats it.
  const tools = [
    {
      id: 'units',
      title: 'Unit systems',
      io: 'one value → SI, SI (mm), US (ft), US (in)',
      text: 'Type a value in the highlighted system; the other three follow.',
      component: SiConversionCard
    },
    {
      id: 'isotropic',
      title: 'Isotropic elastic constants',
      io: 'two of K, G, E, ν, M, λ → all six',
      text: 'Enter exactly two constants to get the other four.',
      component: ConversionCard
    },
    {
      id: 'orthotropic',
      title: 'Orthotropic matrix',
      io: 'nine E, G, ν → 6×6 Cij',
      text: 'Enter all nine engineering constants. Click a matrix entry to copy it.',
      component: StiffnessCard
    },
    {
      id: 'amplitude',
      title: 'Load amplitude',
      io: 'shape, bounds, frequency → f(t)',
      text: 'Shape a load curve over time and copy the expression into a boundary condition.',
      component: AmplitudeCard
    }
  ];
</script>

<svelte:head>
  <title>Tools — PeriHub</title>
</svelte:head>

<div class="bg-background text-foreground">
  <div class="mx-auto max-w-6xl px-6 pt-12 pb-20 sm:pt-16">
    <header class="max-w-2xl">
      <h1
        class="font-display text-3xl leading-none font-extrabold tracking-tight sm:text-4xl"
        style="font-stretch: 125%"
      >
        Tools
      </h1>
      <p class="text-muted-foreground mt-3 text-balance">
        Quick calculations for setting up a model: convert units, derive elastic constants and shape
        a load curve.
      </p>
    </header>

    <div class="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[14rem_minmax(0,1fr)]">
      <nav aria-label="Tools" class="lg:sticky lg:top-6 lg:self-start">
        <ul
          class="border-border flex gap-x-6 gap-y-3 overflow-x-auto border-b pb-3 lg:flex-col lg:border-b-0 lg:border-l lg:pb-0"
        >
          {#each tools as t (t.id)}
            <li class="shrink-0">
              <a
                href="#{t.id}"
                class="group block focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B] lg:-ml-px lg:border-l-2 lg:border-transparent lg:pl-4 lg:hover:border-[#00658B]"
              >
                <span class="dark:group-hover:text-primary font-medium group-hover:text-[#00658B]"
                  >{t.title}</span
                >
                <span class="hidden font-mono text-xs opacity-60 lg:block">{t.io}</span>
              </a>
            </li>
          {/each}
        </ul>
      </nav>

      <div>
        {#each tools as t (t.id)}
          <section
            id={t.id}
            aria-labelledby="{t.id}-heading"
            class="border-border scroll-mt-6 border-t py-10 first:border-t-0 first:pt-0"
          >
            <p class="dark:text-primary font-mono text-xs tracking-wide text-[#00658B]">{t.io}</p>
            <h2 id="{t.id}-heading" class="mt-1 text-2xl font-semibold tracking-tight">
              {t.title}
            </h2>
            <p class="text-muted-foreground mt-1 mb-5">{t.text}</p>
            <t.component />
          </section>
        {/each}
      </div>
    </div>
  </div>
</div>
