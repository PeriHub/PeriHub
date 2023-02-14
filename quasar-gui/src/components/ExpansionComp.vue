<template>
    <ModelSettings></ModelSettings>
</template>

<script>
import { defineComponent } from 'vue'
import ModelSettings from 'components/expansions/Model.vue'

export default defineComponent({
    name: "ExpansionComp",
    components: {
        ModelSettings
    },
})
</script>