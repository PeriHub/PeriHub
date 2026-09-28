<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import Prism from 'prismjs';
  import 'prismjs/components/prism-clike';
  import 'prismjs/components/prism-javascript';
  import 'prismjs/components/prism-yaml';
  import 'prismjs/components/prism-python';
  import 'prismjs/themes/prism-tomorrow.css';

  interface Props {
    value: string;
    editable?: boolean;
    language?: string;
    class?: string;
  }

  let {
    value = $bindable(),
    editable = true,
    language = 'javascript',
    class: className = ''
  }: Props = $props();

  const highlighted = $derived(
    Prism.highlight(value ?? '', Prism.languages[language] ?? Prism.languages.javascript!, language)
  );

  // Editing: a transparent <textarea> over the highlighted <pre>, both in the same grid cell so
  // the text sets the height and the outer box scrolls. The textarea owns the text, so cursor,
  // selection and undo survive re-highlighting (a contenteditable whose HTML is replaced on
  // every keystroke loses them).
  const layer =
    'col-start-1 row-start-1 m-0 p-3 font-mono text-sm leading-normal whitespace-pre-wrap break-words';
</script>

{#if editable}
  <div
    class="border-border grid min-h-[200px] w-full grid-cols-1 overflow-auto rounded-md border bg-[#2d2d2d] text-white {className}"
  >
    <!-- The trailing space keeps a final empty line as tall as in the textarea. -->
    <!-- eslint-disable-next-line svelte/no-at-html-tags -->
    <pre aria-hidden="true" class="{layer} pointer-events-none">{@html highlighted}{' '}</pre>
    <textarea
      bind:value
      spellcheck="false"
      autocapitalize="off"
      autocomplete="off"
      class="{layer} resize-none overflow-hidden border-0 bg-transparent text-transparent caret-white outline-none selection:bg-white/25"
    ></textarea>
  </div>
{:else}
  <pre
    class="language-{language} border-border min-h-[200px] w-full overflow-auto rounded-md border bg-[#2d2d2d] p-3 font-mono text-sm {className}">
  <!-- eslint-disable-next-line svelte/no-at-html-tags -->
   <code>{@html highlighted}</code></pre>
{/if}
