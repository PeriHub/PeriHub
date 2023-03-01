<template>
    <!-- <q-img
        :src="viewStore.modelImg"
        alt="QZoom basic"
        class="my-image"
    /> -->
    <vue-image-zoomer
        :regular="viewStore.modelImg"
        :zoom-amount="3"
        :click-zoom="true"
        img-class="my-image"
        alt="Grass"/>
   <!-- <q-img
        scale-down
        :src="viewStore.modelImg"
        width="100%"
        height="100%"
    /> -->
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
.my-image{
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 100%;
  margin: auto}
</style>
