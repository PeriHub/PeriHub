<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import ConversionCard from '$lib/components/tools/ConversionCard.svelte';
  import SiConversionCard from '$lib/components/tools/SiConversionCard.svelte';
  import StiffnessCard from '$lib/components/tools/StiffnessCard.svelte';
  import AmplitudeCard from '$lib/components/tools/AmplitudeCard.svelte';
</script>

<svelte:head>
  <title>Tools — PeriHub</title>
</svelte:head>

<div class="mx-auto flex max-w-5xl flex-col items-center gap-8 px-6 py-10">
  <SiConversionCard />
  <ConversionCard />
  <StiffnessCard />
  <AmplitudeCard />
</div>
