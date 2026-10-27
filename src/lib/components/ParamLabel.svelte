<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  Label of a PeriLab key: the YAML key itself, `*` when required, and PeriLab's description/facts behind an info
  icon (InfoTip renders them sr-only under `descId` for the field's aria-describedby).
-->
<script lang="ts">
  import { propInfo, type SchemaProp } from '$lib/perilab/schema';
  import InfoTip from '$lib/components/ui/InfoTip.svelte';
  import Label from '$lib/components/ui/Label.svelte';

  interface Props {
    key: string;
    prop?: SchemaProp;
    for: string;
    required?: boolean;
    descId?: string;
  }

  let { key, prop, for: htmlFor, required = false, descId }: Props = $props();
  const about = $derived(prop ? propInfo(prop) : { text: '', facts: [] });
</script>

<div class="flex items-center gap-1.5">
  <Label for={htmlFor}>
    {key}{#if required}<span class="text-destructive" aria-hidden="true"> *</span>{/if}
  </Label>
  {#if about.text || about.facts.length}
    <InfoTip title={key} text={about.text} facts={about.facts} id={descId} />
  {/if}
</div>
