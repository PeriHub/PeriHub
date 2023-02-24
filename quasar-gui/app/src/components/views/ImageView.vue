<template>
   <q-img
        alt="DLR Logo"
        class="shrink mr-2"
        contain
        :src="viewStore.modelImg"
        transition="scale-transition"
        width="100%"
        height="100%"
    />
</template>

<script>
    import { defineComponent } from 'vue'
    import { useViewStore } from 'stores/view-store';
    export default defineComponent({
        name: 'ImageView',
        setup() {
            const viewStore = useViewStore();

            return {
                viewStore
            }
        },
        data() {
            return {
            };
        },
        methods: {},
    })
</script>

<style>
</style>
