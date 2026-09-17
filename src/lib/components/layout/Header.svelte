<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { DropdownMenu } from 'bits-ui';
import Button from '$lib/components/ui/Button.svelte';
  import {
    Compass, Github, Youtube, Zap, Moon, Sun, Leaf, User,
    HelpCircle, MoreVertical, Award, Clock, ExternalLink
  } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { getLicenseStatus } from '$lib/client';
  import UserSettingsDialog from '$lib/components/dialogs/UserSettingsDialog.svelte';
  import PlanDialog from '$lib/components/dialogs/PlanDialog.svelte';

  const navItems = [
    { href: '/perihub', label: 'PeriHub' },
    { href: '/models', label: 'Models' },
    { href: '/tools', label: 'Tools' },
    { href: '/publications', label: 'Publications' }
  ];

  // External/secondary links, consolidated into one menu instead of four
  // separate icon-only buttons so the toolbar stays usable on narrow
  // screens and each link gets a visible, accessible label.
  const links = [
    { href: 'https://perihub.github.io/PeriHub/', label: 'Documentation', icon: Compass },
    { href: 'https://github.com/PeriHub/PeriHub', label: 'GitHub', icon: Github },
    { href: '/api/docs', label: 'PeriHub API', icon: Zap },
    { href: 'https://www.youtube.com/@PeriHub', label: 'YouTube', icon: Youtube }
  ];

  let dialogOpen = $state(false);
  let dialogPlan = $state(false);

  // Real plan, read from the license server via GET /license/status
  // (support/license_client.py + entitlements.py on the backend). Falls
  // back to "community" if the request fails, same as the backend's own
  // fail-open (nothing gated) behaviour with no license server configured.
  let plan = $state('community');

  async function fetchPlan() {
    try {
      const status = await getLicenseStatus();
      plan = status.plan;
    } catch {
      plan = 'community';
    }
  }

  const planLabel = $derived(plan.charAt(0).toUpperCase() + plan.slice(1));
  const planColor = $derived(
    plan === 'enterprise'
      ? 'bg-success/25 text-success'
      : plan === 'trial'
        ? 'bg-warning/25 text-warning'
        : 'bg-white/15'
  );
  const PlanIcon = $derived(plan === 'enterprise' ? Award : plan === 'trial' ? Clock : Leaf);

  onMount(fetchPlan);

  function isActive(href: string) {
    return $page.url.pathname.startsWith(href);
  }

  function toggleDarkMode() {
    defaultStore.toggleDarkMode();
  }

  function toggleSaveEnergy() {
    defaultStore.saveEnergy = !defaultStore.saveEnergy;
    if (typeof window !== 'undefined') {
      localStorage.setItem('saveEnergy', String(defaultStore.saveEnergy));
    }
  }

  function takeTour() {
    bus.emit('showTutorial' as never);
  }

  const iconButtonClass =
    'flex h-9 w-9 shrink-0 items-center justify-center rounded-full hover:bg-white/10 hover:outline hover:outline-1 hover:outline-white/30 transition-colors';
</script>

<header
  class="sticky top-0 z-40 border-b border-primary/20 bg-primary text-primary-foreground shadow-sm"
>
  <div class="relative mx-auto flex h-16 max-w-7xl items-center gap-2 px-3 sm:px-6">
    <!-- Logo -->
    <a href="/" class="z-10 flex shrink-0 items-center gap-2 no-underline" aria-label="PeriHub home">
      <img
        src="/PeriHubLogo2b.png"
        alt="PeriHub"
        width="44"
        height="44"
        class="h-11 w-11 shrink-0 object-contain"
      />
    </a>

    <nav class="absolute left-1/2 -translate-x-1/2 flex items-center gap-3 md:flex">
      {#each navItems as item (item.href)}
        <Button
          href={item.href}
          variant="ghost"
          size="lg"
        >
          {item.label}
        </Button>
      {/each}
    </nav>

    <div class="absolute right-0 ml-auto flex items-center gap-1.5">
      <!-- Plan / licensing indicator, backed by the real /license/status endpoint. -->
      <Button
        type="button"
        variant="outline"
        size="sm"
        class="hidden rounded-full px-3 py-1.5 text-xs font-medium hover:brightness-110 sm:flex {planColor}"
        onclick={() => (dialogPlan = true)}
        title="Plan & licensing"
        aria-label={`Current plan: ${planLabel}. Open plan and licensing details`}
      >
        <PlanIcon class="h-3.5 w-3.5" />
        {planLabel}
      </Button>

      <!-- Persistent, visible help entry point: the product tour was previously
           only reachable via a small info icon buried in the Model panel, so
           first-time users who missed it had no other way to find it. -->
      <Button
        variant="ghost"
        size="icon"
        class={iconButtonClass}
        onclick={takeTour}
        title="Take the tour"
        aria-label="Take the tour"
      >
        <HelpCircle class="h-5 w-5" />
      </Button>

      <!-- Core preference toggles: always visible, not gated behind a
           breakpoint, so they can't silently disappear at any viewport size. -->
      <Button
        variant="ghost"
        size="icon"
        class={iconButtonClass}
        onclick={toggleSaveEnergy}
        title={defaultStore.saveEnergy ? 'Renewable energy check: on' : 'Renewable energy check: off'}
        aria-label="Check renewable energy availability before submitting simulations"
        aria-pressed={defaultStore.saveEnergy}
      >
        {#if defaultStore.saveEnergy}
          <Leaf class="h-5 w-5 text-green-300" />
        {:else}
          <Zap class="h-5 w-5 text-yellow-300" />
        {/if}
      </Button>

      <Button
        variant="ghost"
        size="icon"
        class={iconButtonClass}
        onclick={toggleDarkMode}
        title={defaultStore.darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        aria-label={defaultStore.darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        aria-pressed={defaultStore.darkMode}
      >
        {#if defaultStore.darkMode}
          <Moon class="h-5 w-5" />
        {:else}
          <Sun class="h-5 w-5" />
        {/if}
      </Button>

      <!-- Secondary/external links: grouped into one menu instead of four separate
           icon-only buttons, so the toolbar stays usable on narrow screens. -->
      <DropdownMenu.Root>
        <DropdownMenu.Trigger
          class={iconButtonClass}
          title="Links & resources"
          aria-label="Links & resources"
        >
          <MoreVertical class="h-5 w-5" />
        </DropdownMenu.Trigger>
        <DropdownMenu.Portal>
          <DropdownMenu.Content
            class="z-50 min-w-[200px] rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md"
            align="end"
          >
            {#each links as link (link.href)}
              <DropdownMenu.Item class="flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-muted">
                {#snippet child({ props })}
                  <a {...props} href={link.href} target={link.href.startsWith('http') ? '_blank' : undefined} rel="noopener">
                    <link.icon class="h-4 w-4" />
                    {link.label}
                    {#if link.href.startsWith('http')}
                      <ExternalLink class="ml-auto h-3 w-3 opacity-60" />
                    {/if}
                  </a>
                {/snippet}
              </DropdownMenu.Item>
            {/each}
          </DropdownMenu.Content>
        </DropdownMenu.Portal>
      </DropdownMenu.Root>

      <Button
        variant="ghost"
        size="icon"
        class="ml-0.5 flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-white/15 hover:bg-white/25"
        onclick={() => (dialogOpen = true)}
        title="User settings"
        aria-label="Open user settings"
      >
        {#if defaultStore.useGravatar}
          <img src={defaultStore.gravatarUrl} alt="User avatar" width="36" height="36" class="h-full w-full object-cover" />
        {:else}
          <User class="h-5 w-5" />
        {/if}
      </Button>
    </div>
  </div>
</header>

<UserSettingsDialog bind:open={dialogOpen} />
<PlanDialog bind:open={dialogPlan} />
