<template>
    <q-page class="flex-center">
        <ConversionCard/>
        <SiConversionCard/>
    </q-page>
</template>

<script>
import { defineComponent } from 'vue'
import ConversionCard from 'components/tools/ConversionCard.vue'
import SiConversionCard from 'components/tools/SiConversionCard.vue'

export default defineComponent({
    name: "GuidePage",
    components: {
        ConversionCard,
        SiConversionCard,
    },
});
</script>

<style>
</style>