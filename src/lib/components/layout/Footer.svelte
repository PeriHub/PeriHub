<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import Button from '$lib/components/ui/Button.svelte';

  const links = [
    { label: 'About us', href: 'https://www.dlr.de/sy' },
    { label: 'Blog', href: 'https://leichtbau.dlr.de/' },
    { label: 'Contact us', href: 'mailto:Jan-Timo.Hesse@dlr.de' },
    { label: 'Impressum', href: '/impressum' },
    { label: 'Privacy policy', href: '/privacy' },
    { label: 'Terms of use', href: '/copyright' },
    { label: 'Accessibility statement', href: '/accessibility' }
  ];

  const year = new Date().getFullYear();
</script>

<footer class="border-t border-primary/20 bg-primary text-primary-foreground">
  <div class="mx-auto flex max-w-7xl flex-col items-center gap-2 px-4 py-4 text-center">
    <nav class="flex flex-wrap items-center justify-center gap-3 text-[11px] font-medium sm:text-xs">
      {#each links as link (link.href)}
        <Button href={link.href} variant="ghost" size="sm" class="uppercase tracking-wide opacity-90 hover:opacity-100 hover:text-white">
          {link.label}
        </Button>
      {/each}
    </nav>
    <p class="text-xs opacity-90 sm:text-sm">
      © {year} German Aerospace Center (DLR) — <strong>PeriHub</strong> | Jan-Timo Hesse | Christian
      Willberg
    </p>
  </div>
</footer>
