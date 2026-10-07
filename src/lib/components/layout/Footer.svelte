<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
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

<footer class="bg-brand text-brand-foreground border-t border-white/10">
  <div
    class="mx-auto flex max-w-7xl flex-col items-center gap-x-6 gap-y-2 px-4 py-4 text-xs md:flex-row md:justify-between"
  >
    <div class="flex items-center gap-3">
      <a href="https://www.dlr.de" class="shrink-0 opacity-80 hover:opacity-100">
        <img src="/DLR_Signet_weiss.png" alt="German Aerospace Center (DLR)" class="h-8 w-auto" />
      </a>
      <p class="opacity-80">
        © {year} German Aerospace Center (DLR) · <strong>PeriHub</strong> · Jan-Timo Hesse, Christian
        Willberg
      </p>
    </div>
    <nav class="flex flex-wrap justify-center gap-x-4 gap-y-1" aria-label="Footer">
      {#each links as link (link.href)}
        <a href={link.href} class="opacity-80 hover:underline hover:opacity-100">{link.label}</a>
      {/each}
    </nav>
  </div>
</footer>
