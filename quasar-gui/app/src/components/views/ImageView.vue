<template>
    <vue-image-zoomer
        :regular="viewStore.modelImg"
        :zoom-amount="3"
        :click-zoom="true"
        img-class="my-image"
        alt="ModelImag"/>
</template>

<script>
    import { defineComponent, inject } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { useViewStore } from 'stores/view-store';

    import KIICmodelImage from "assets/models/KIICmodel/KIICmodel.jpg";
    import GIICmodelImage from "assets/models/GIICmodel/GIICmodel.jpg";
    import GICmodelImage from "assets/models/GICmodel/GICmodel.jpg";
    import DCBmodelImage from "assets/models/DCBmodel/DCBmodel.jpg";
    import DogboneImage from "assets/models/Dogbone/Dogbone.jpg";
    import KalthoffWinklerImage from "assets/models/Kalthoff-Winkler/Kalthoff-Winkler.jpg";
    import PlateWithHoleImage from "assets/models/PlateWithHole/PlateWithHole.jpg";
    import CompactTensionImage from "assets/models/CompactTension/CompactTension.jpg";
    import SmetanaImage from "assets/models/Smetana/Smetana.jpg";

    export default defineComponent({
        name: 'ImageView',
        setup() {
            const modelStore = useModelStore();
            const viewStore = useViewStore();
            const bus = inject('bus')
            return {
                modelStore,
                viewStore,
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
                switch (modelName) {
                    case "GICmodel":
                    this.viewStore.modelImg = GICmodelImage;
                    break;
                    case "GIICmodel":
                    this.viewStore.modelImg = GIICmodelImage;
                    break;
                    case "KIICmodel":
                    this.viewStore.modelImg = KIICmodelImage;
                    break;
                    case "DCBmodel":
                    this.viewStore.modelImg = DCBmodelImage;
                    break;
                    case "Dogbone":
                    this.viewStore.modelImg = DogboneImage;
                    break;
                    case "Kalthoff-Winkler":
                    this.viewStore.modelImg = KalthoffWinklerImage;
                    break;
                    case "PlateWithHole":
                    this.viewStore.modelImg = PlateWithHoleImage;
                    break;
                    case "CompactTension":
                    this.viewStore.modelImg = CompactTensionImage;
                    break;
                    case "Smetana":
                    this.viewStore.modelImg = SmetanaImage;
                    break;
                }
                this.viewStore.viewId = "image";
            },
        },
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
