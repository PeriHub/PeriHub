<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="flex-center">
    <ConversionCard />
    <SiConversionCard />
    <StiffnessCard />
    <AmplitudeCard />
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import ConversionCard from 'components/tools/ConversionCard.vue'
import SiConversionCard from 'components/tools/SiConversionCard.vue'
import StiffnessCard from 'components/tools/StiffnessCard.vue'
import AmplitudeCard from 'components/tools/AmplitudeCard.vue'

export default defineComponent({
  name: "ToolsPage",
  components: {
    ConversionCard,
    SiConversionCard,
    StiffnessCard,
    AmplitudeCard
  },
});
</script>

<style></style>
