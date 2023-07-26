<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <q-page class="flex-center">
        <ConversionCard />
        <SiConversionCard />
        <StiffnessCard />
    </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import ConversionCard from 'components/tools/ConversionCard.vue'
import SiConversionCard from 'components/tools/SiConversionCard.vue'
import StiffnessCard from 'components/tools/StiffnessCard.vue'

export default defineComponent({
    name: "GuidePage",
    components: {
        ConversionCard,
        SiConversionCard,
        StiffnessCard
    },
});
</script>

<style></style>