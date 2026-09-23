<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  const cards = [
    { title: 'PeriHub', href: '/perihub', img: '/dogbone.png' },
    { title: 'Guide', href: 'https://perihub.github.io/PeriHub/', img: '/compass.png' },
    { title: 'Publications', href: '/publications', img: '/books.png' },
    { title: 'Tools', href: '/tools', img: '/tools.png' },
    { title: 'API', href: '/api/docs', img: 'https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png' },
    {
      title: 'GitHub',
      href: 'https://github.com/PeriHub/PeriHub',
      img: 'https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png'
    },
    {
      title: 'PeriLab-Results',
      href: 'https://perilab-results.nimbus-extern.dlr.de',
      img: '/perilab.png'
    },
    {
      title: 'YouTube',
      href: 'https://www.youtube.com/@PeriHub',
      img: 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png'
    }
  ];
</script>

<svelte:head>
  <title>PeriHub</title>
</svelte:head>

<section class="mx-auto max-w-3xl px-6 pb-8 pt-16 text-center">
  <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">Welcome to PeriHub</h1>
  <p class="mt-5 text-balance text-muted-foreground">
    PeriHub is a platform that provides a numerical implementation of the peridynamic theory. It
    is an extension of the open source PeriLab software. Peridynamics is a non-local theory that
    overcomes discontinuity problems of the classical theory of continuum mechanics — an effective
    method for modeling fracture mechanics problems.
  </p>
</section>

<section class="mx-auto grid max-w-6xl grid-cols-1 gap-5 px-6 pb-16 sm:grid-cols-2 lg:grid-cols-4">
  {#each cards as card (card.title)}
    <a
      href={card.href}
      class="group relative block h-44 overflow-hidden rounded-xl border border-border bg-muted shadow-sm transition-transform hover:-translate-y-0.5 hover:shadow-md"
    >
      <img
        src={card.img}
        alt={card.title}
        class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/0 to-transparent"></div>
      <div class="absolute bottom-0 right-0 p-3 text-right text-lg font-semibold text-white">
        {card.title}
      </div>
    </a>
  {/each}
</section>
