<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import SchemaForm from '$lib/components/SchemaForm.svelte';

  const job = $derived(modelStore.modelData.job);

  $effect(() => {
    if (!job.cluster) {
      job.tasks = 1;
    }
  });
</script>

<!--
  All of this panel's fields (verbose/cluster/sbatch, then the cluster- and
  sbatch-conditional ones) are rendered by SchemaForm straight from the
  `Job` schema's yaml_field(...) metadata in backend/app/support/base_models.py
  - adding a new Job field only means editing that one model; no new markup
  needed here unless the field needs a genuinely new conditional-visibility
  rule (like the cluster/sbatch gating below, which is real component logic
  and stays hand-written on purpose - see SchemaForm.svelte's docstring).
-->
<div class="space-y-3 p-3">
  <SchemaForm schemaName="Job" data={job} group="Job" disabledFields={defaultStore.trial ? ['cluster', 'sbatch'] : []} />

  {#if job.cluster}
    <SchemaForm schemaName="Job" data={job} group="JobCluster" />
  {/if}

  {#if job.sbatch}
    <SchemaForm schemaName="Job" data={job} group="JobSbatch" />
  {/if}
</div>
