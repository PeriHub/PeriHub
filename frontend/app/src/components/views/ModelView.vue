<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div style="height:calc(100% - 60px);">
    <div class="row">
      <div style="width: 100px;">
        <q-btn v-if="!modelData.modelownModel" flat icon="fas fa-sync-alt" @click="viewPointData">
          <q-tooltip>
            Reload Model
          </q-tooltip>
        </q-btn>
        <q-btn v-if="!modelData.modelownModel" flat icon="fas fa-expand" @click="$refs.view.resetCamera()">
          <q-tooltip>
            Reset Camera
          </q-tooltip>
        </q-btn>
      </div>
      <div style="min-width: 100px; margin-right:20px">
        <q-slider v-model="multiplier" :min="1" :max="200" :step="1" label :label-value="'Radius: ' + multiplier + ' %'"
          switch-label-side @change="updatePoints" color="gray"></q-slider>
      </div>
      <!-- <div class="col" style="width: 100px;">
      </div> -->
      <div style="min-width: 100px;">
        <q-slider v-model="resolution" :min="3" :max="20" :step="1" label :label-value="'Resolution: ' + resolution"
          switch-label-side color="gray"></q-slider>
      </div>
    </div>
    <vtk-view ref="view" :background="[45 / 255, 45 / 255, 45 / 255]">
      <div v-if="viewStore.bondFilterPoints.length != 0">
        <q-list v-for="bondFilterPoint in viewStore.bondFilterPoints" :key="bondFilterPoint.id">
          <vtk-geometry-representation>
            <vtk-polydata :points="bondFilterPoint.bondFilterPointString" :polys="[4, 0, 1, 2, 3]">
              <vtk-point-data>
                <vtk-data-array registration="setScalars" name="temperature" :values="[.8, .8, .8, .8]" />
              </vtk-point-data>
            </vtk-polydata>
          </vtk-geometry-representation>
        </q-list>
      </div>
      <vtk-glyph-representation>
        <vtk-polydata :points="viewStore.filteredPointString">
          <vtk-cell-data>
            <vtk-data-array registration="setScalars" name="scalars" :values="viewStore.filteredBlockIdString"
              :state="{ rangeMax: 100, rangeMin: -100 }" />
          </vtk-cell-data>
        </vtk-polydata>
        <vtk-algorithm vtkClass="vtkSphereSource"
          :state="{ phiResolution: resolution, thetaResolution: resolution, radius: radius * multiplier / 100 }"
          :port="1" />
      </vtk-glyph-representation>
    </vtk-view>
  </div>
</template>

<script>
import { inject, computed, defineComponent } from 'vue'
import { useViewStore } from 'src/stores/view-store';
import { useModelStore } from 'src/stores/model-store';
import { getPointData } from 'src/client';

export default defineComponent({
  name: 'ModelView',
  components: {
  },
  setup() {
    const viewStore = useViewStore();
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)
    const bus = inject('bus')
    return {
      viewStore,
      modelStore,
      modelData,
      bus,
    }
  },
  created() {
    console.log('createdModelView')
  },
  unmounted() {
    console.log('unmountedModelView')
    this.bus.off('viewPointData');
    this.bus.off('filterPointData');
  },
  data() {
    return {
      resolution: 6,
      radius: 0.2,
      multiplier: 100,
      pointString: [1, 0, 0],
      blockIdString: [1],
    };
  },
  mounted() {
    console.log('ModelView mounted')
    this.bus.once('viewPointData', async () => {
      await this.viewPointData()
    })
    this.bus.on('filterPointData', () => {
      this.filterPointData()
    })
    // this.viewPointData()
  },
  methods: {
    async viewPointData() {
      console.log('viewPointData')
      this.viewStore.modelLoading = true;

      await this.getPointDataAndUpdateDx();
      this.radius = parseFloat(this.viewStore.dx_value.toFixed(3));
      await this.updatePoints();
      this.bus.emit('showHideBondFilters');

      this.viewStore.modelLoading = false;
      // console.log(this.$refs)
      this.$refs.view.resetCamera();
    },
    filterPointData() {
      console.log('filterPointData')
      var idx = 0;
      let filteredBlockIdStringTemp = [];
      let filteredPointStringTemp = [];
      const blocks = this.modelData.blocks
      for (var i = 0; i < this.blockIdString.length; i++) {
        if (
          blocks[parseInt(this.blockIdString[i] * this.modelData.blocks.length - 1)].show
        ) {
          filteredBlockIdStringTemp[idx] = this.blockIdString[i];
          for (var j = 0; j < 3; j++) {
            filteredPointStringTemp[idx * 3 + j] = this.pointString[i * 3 + j];
            // this.pointString[i * 3 + j] * this.multiplier;
          }
          idx += 1;
        }
      }
      this.viewStore.filteredBlockIdString = filteredBlockIdStringTemp;
      this.viewStore.filteredPointString = filteredPointStringTemp;
    },
    async updatePoints() {
      this.viewStore.modelLoading = true;
      console.log('updatePoints')
      // if (this.radius < 0.01) {
      //   this.multiplier = (1 - this.radius / 0.5) * 30;
      //   this.radius=0.01
      // } else if (this.radius <= 0.2) {
      //   this.multiplier = (1 - this.radius / 0.5) * 30;
      // } else {
      //   this.multiplier = 1;
      // }
      this.filterPointData();
      this.viewStore.modelLoading = false;
    },
    async getPointDataAndUpdateDx() {

      console.log('getPointDataAndUpdateDx')
      await getPointData({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        ownModel: this.modelData.model.ownModel,
        ownMesh: this.modelData.model.ownMesh,
        meshFile: this.modelData.model.meshFile,
        twoD: this.modelData.model.twoDimensional
      })
        .then((response) => {
          this.pointString = response.data[0].split(',')
          this.blockIdString = response.data[1].split(',')
          this.$q.notify({
            message: response.message,
          })
        })
        .catch(() => {
          this.$q.notify({
            type: 'negative',
            message: 'Loading failed',
          })
        })

      // if (!this.modelData.model.ownModel) {
      //   this.viewStore.dx_value =
      //     this.modelData.model.height / (2 * parseInt(this.modelData.model.discretization / 2) + 1);
      if (this.modelData.model.modelNameSelected == 'Smetana') {
        let numOfPlys = 8;
        this.viewStore.dx_value =
          (this.modelData.model.height * numOfPlys) /
          (2 * parseInt(this.modelData.model.discretization / 2) + 1);
      } else {
        this.viewStore.dx_value = Math.hypot(
          parseFloat(this.pointString[3]) - parseFloat(this.pointString[0]),
          parseFloat(this.pointString[4]) - parseFloat(this.pointString[1]),
          parseFloat(this.pointString[5]) - parseFloat(this.pointString[2])
        );
      }

      // if (this.modelData.model.modelNameSelected == "Smetana") {
      //   var blockIdInt = this.blockIdString.map(Number);
      //   let numberOfBlocks = Math.max(...blockIdInt);
      //   for (var i = 0; i < numberOfBlocks; i++) {
      //     if (this.blocks.length < i + 1) {
      //       this.addBlock();
      //     }
      //   }
      //   if (this.blocks.length > numberOfBlocks) {
      //     for (var j = numberOfBlocks; j < this.blocks.length; j++) {
      //       this.removeBlock(j);
      //     }
      //   }
      // }
    },
  },
})
</script>

<style>
.viewport {
  height: 100%;
  width: 100%;
}
</style>
