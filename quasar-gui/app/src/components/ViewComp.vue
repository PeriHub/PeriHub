<template>
    <div style="height:100%">
        <ImageView v-if="store.viewId==0"></ImageView>
        <ModelView v-if="store.viewId==1"></ModelView>
        <PlotlyView v-if="store.viewId==2"></PlotlyView>
    </div>
</template>

<script>
import { defineComponent } from 'vue'
import ImageView from 'components/views/ImageView.vue'
import ModelView from 'components/views/ModelView.vue'
import PlotlyView from 'components/views/PlotlyView.vue'
import { useViewStore } from 'stores/view-store';

export default defineComponent({
    name: "ViewComp",
    components: {
        ImageView,
        ModelView,
        PlotlyView
    },
    setup() {
        const store = useViewStore();
        return {
            store,
        }
    },
})
</script>