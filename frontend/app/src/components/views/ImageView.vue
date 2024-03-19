<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <vue-image-zoomer :regular="viewStore.modelImg" :zoom-amount="3" :click-zoom="true" img-class="my-image"
        alt="ModelImag" />
</template>

<script>
import { defineComponent, inject } from 'vue'
import { useModelStore } from 'stores/model-store';
import { useViewStore } from     tores/view-store';

    port default        ineComponent({
             e: 'Image                   setup() {
        const modelStore = useModelS            ;
               ons    viewStore         eViewStore();
        const bus =        ect('bus'                ret        {
                mode        re,
                    ewStore,
            bus
        }
    },
    created() {
        this.bus.on('showModelImg', (modelName) => {
            this.showModelImg(modelName)
        })
    },
    methods: {
        showModelImg(modelName) {
            this.viewStore.modelImg = process.env.API + "/assets/models/" + modelName + "/" + modelName + ".jpg";

            this.viewStore.viewId = "image";
        },
    },
})
</script>

<style>
.my-image {
    width: 100%;
    height: auto;
    max-width: 100%;
    max-height: 100%;
    margin: auto
}
</style>
