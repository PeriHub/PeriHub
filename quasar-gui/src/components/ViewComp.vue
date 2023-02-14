<template>
    <PlotlyView></PlotlyView>
</template>

<script>
import { defineComponent } from 'vue'
// import ModelView from 'components/views/ModelView.vue'
import PlotlyView from 'components/views/PlotlyView.vue'

export default defineComponent({
    name: "ViewComp",
    components: {
        // ModelView,
        PlotlyView
    },
})
</script>