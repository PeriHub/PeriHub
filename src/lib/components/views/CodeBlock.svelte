<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import Prism from 'prismjs';
  import 'prismjs/components/prism-clike';
  import 'prismjs/components/prism-javascript';
  // @ts-expect-error no types shipped for this submodule
  import 'prismjs/components/prism-yaml';
  // @ts-expect-error no types shipped for this submodule
  import 'prismjs/components/prism-python';
  import 'prismjs/themes/prism-tomorrow.css';

  interface Props {
    value: string;
    editable?: boolean;
    language?: string;
    class?: string;
  }

  let { value = $bindable(), editable = true, language = 'javascript', class: className = '' }: Props =
    $props();

  let highlighted = $state('');

  function highlight(code: string) {
    const grammar = Prism.languages[language] ?? Prism.languages.javascript;
    return Prism.highlight(code, grammar, language);
  }

  $effect(() => {
    highlighted = highlight(value);
  });

  function onInput(e: Event) {
    value = (e.target as HTMLElement).innerText;
  }

  let mounted = false;
  onMount(() => (mounted = true));
</script>

{#if editable}
  <div
    class="prism-editor language-{language} min-h-[200px] w-full overflow-auto rounded-md border border-border bg-[#2d2d2d] p-3 font-mono text-sm text-white outline-none {className}"
    contenteditable="plaintext-only"
    spellcheck="false"
    oninput={onInput}
  >{@html mounted ? highlighted : value}</div>
{:else}
  <pre
    class="language-{language} min-h-[200px] w-full overflow-auto rounded-md border border-border bg-[#2d2d2d] p-3 font-mono text-sm {className}"
  ><code>{@html highlighted}</code></pre>
{/if}

<style>
  .prism-editor :global(*) {
    white-space: pre-wrap;
  }
</style>
