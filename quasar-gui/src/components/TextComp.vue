<template>
    <div style="height:100%">
        <TextView></TextView>
    </div>
</template>

<script>
import { defineComponent } from 'vue'
import TextView from 'components/views/TextView.vue'
import { useViewStore } from 'stores/view-store';

export default defineComponent({
    name: "TextComp",
    components: {
        TextView
    },
    setup() {
        const store = useViewStore();
        return {
            store,
        }
    },
})
</script>