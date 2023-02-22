<template>
   <q-img
        alt="DLR Logo"
        class="shrink mr-2"
        contain
        :src="modelImg"
        transition="scale-transition"
        width="100%"
        height="100%"
    />
</template>

<script>
    import { defineComponent } from 'vue'
    import DogboneImage from "assets/models/Dogbone/Dogbone.jpg";
    export default defineComponent({
        name: 'ImageView',
        components:{
        },
        data() {
            return {
                modelImg: DogboneImage,
            };
        },
        methods: {},
    })
</script>

<style>
</style>
