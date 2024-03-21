<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div style="height: 100%; width: 100%; overflow: hidden">
    <div style="height:100%;">
      <div class="row" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'">
        <q-btn flat dense icon="fas fa-sync-alt" @click="viewPointData">
          <q-tooltip>
            Reload Model
          </q-tooltip>
        </q-btn>
        <q-btn flat dense icon="fas fa-expand" @click="$refs.view.resetCamera()">
          <q-tooltip>
            Reset Camera
          </q-tooltip>
        </q-btn>
        <div>
          <q-item>
            <q-item-section style="width: 10px; margin-right:20px" side>
              <q-icon color=" #cfcfcf" name="fas fa-clock" />
            </q-item-section>
            <q-item-section>
              <q-slider style="width: 100px" v-model="modelParams.step" :min="1" :max="modelParams.numberOfSteps"
                :step="1" label :label-value="'Time Step: ' + modelParams.step" switch-label-side color="secondary"
                @change="viewPointData"></q-slider>
            </q-item-section>
            <q-item-section side>
              {{ time }}
            </q-item-section>
          </q-item>
        </div>
        <!-- <div class="settings-column">
          <q-select class="textfield-col" :options="variableOptions" v-model="modelParams.variable" label="Variable"
            outlined dense @update:model-value="viewPointData"></q-select>
        </div>
        <div class="settings-column">
          <q-select class="textfield-col" :options="axisOptions" v-model="modelParams.axis" label="Axis" outlined dense
            @update:model-value="viewPointData"></q-select>
        </div>
        <div class="settings-column">
          <q-input v-model.number="modelParams.displFactor" type="number" label="Displ. Magnitude" outlined dense
            debounce:500 @update:model-value="viewPointData"></q-input>
        </div> -->
        <div>
          <q-item>
            <q-item-section style="width: 10px; margin-right:20px" side>
              <q-icon color="#cfcfcf" name="fas fa-up-right-and-down-left-from-center" />
            </q-item-section>
            <q-item-section>
              <q-slider style="width: 100px" v-model="multiplier" :min="1" :max="200" :step="1" label
                :label-value="'Node Size: ' + multiplier + ' %'" switch-label-side @change="updatePoints"
                color="secondary"></q-slider>
            </q-item-section>
          </q-item>
        </div>
        <div>
          <q-item>
            <q-item-section style="width: 10px; margin-right:20px" side>
              <q-icon color="#cfcfcf" name="fas fa-eye" />
            </q-item-section>
            <q-item-section>
              <q-slider style="width: 100px" v-model="resolution" :min="3" :max="20" :step="1" label
                :label-value="'Resolution: ' + resolution" switch-label-side color="secondary"></q-slider>
            </q-item-section>
          </q-item>
        </div>
        <!-- <div class="settings-column">
      <q-toggle v-model="sphere" :label="sphere" false-value="Cube" true-value="Sphere"
        @update:model-value="$refs.view.resetCamera();" />
    </div> -->
      </div>
      <div class="viewport">
        <vtk-view ref="view" :background="[45 / 255, 45 / 255, 45 / 255]">
          <vtk-glyph-representation>
            <vtk-polydata :points="pointString">
              <vtk-cell-data>
                <vtk-data-array registration="setScalars" name="scalars" :values="blockIdString"
                  :state="{ rangeMax: 12 }" />
              </vtk-cell-data>
            </vtk-polydata>
            <vtk-algorithm v-if='sphere == "Sphere"' vtkClass="vtkSphereSource"
              :state="{ phiResolution: resolution, thetaResolution: resolution, radius: radius * multiplier / 100 }"
              :port="1" />
            <!-- <vtk-algorithm v-if='sphere == "Cube"' vtkClass="vtkCubeSource"
            :state="{ XLength: radius * multiplier / 100, YLength: radius * multiplier / 100, ZLength: radius * multiplier / 100 }"
            :port="1" /> -->
          </vtk-glyph-representation>
        </vtk-view>
      </div>
    </div>
    <div class="variables" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'">
      <q-select class="variable" :options="variableOptions" v-model="modelParams.variable" label="Variable" outlined
        dense @update:model-value="viewPointData"></q-select>
      <q-select class="variable" :options="axisOptions" v-model="modelParams.axis" label="Axis" outlined dense
        @update:model-value="viewPointData"></q-select>
      <q-input class="variable" v-model.number="modelParams.displFactor" type="number" label="Displ. Magnitude" outlined
        dense debounce:500 @update:model-value="viewPointData"></q-input>
    </div>
    <vertical-colored-legend class="legend" :min="minValue" :max="maxValue" :key="legendKey" />
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'stores/model-store';
import VerticalColoredLegend from 'src/components/tools/VerticalColoredLegend.vue';
export default {
  name: "PeriLab_Web_Results",
  components: {
    VerticalColoredLegend
  },
  setup() {
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)

    return {
      modelData,
    }
  },
  data() {
    return {
      modelParams: {
        variable: "Displacements",
        axis: "Magnitude",
        displFactor: 1,
        step: 1,
        numberOfSteps: 100
      },
      variableOptions: [
        "Displacements",
        "Damage",
        "Forces"
      ],
      axisOptions: [
        "X",
        "Y",
        "Z",
        "Magnitude"
      ],
      sphere: "Sphere",
      resolution: 6,
      radius: 0.2,
      dx_value: 0.2,
      multiplier: 100,
      pointString: [1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 0, 9, 0, 0, 10, 0, 0, 11, 0, 0],
      blockIdString: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      file: "DCBmodel_Output1.e",
      modelLoading: false,
      drawer: false,
      maxValue: 100,
      minValue: 0,
      legendKey: 0,
      time: 0,
    };
  },

  mounted() {
    console.log("ModelView mounted")
    this.viewPointData()
  },
  methods: {
    async viewPointData() {
      console.log("viewPointData")
      this.modelLoading = true;

      await this.getPointDataAndUpdateDx();
      this.radius = parseFloat(this.dx_value.toFixed(3));
      await this.updatePoints();

      this.modelLoading = false;
      this.$refs.view.resetCamera();
    },
    // filterPointData() {
    //   console.log("filterPointData")
    //   var idx = 0;
    //   let filteredBlockIdStringTemp = [];
    //   let filteredPointStringTemp = [];
    //   const blocks = this.modelData.blocks
    //   for (var i = 0; i < this.blockIdString.length; i++) {
    //     if (
    //       blocks[parseInt(this.blockIdString[i] * this.modelData.blocks.length - 1)].show
    //     ) {
    //       filteredBlockIdStringTemp[idx] = this.blockIdString[i];
    //       for (var j = 0; j < 3; j++) {
    //         filteredPointStringTemp[idx * 3 + j] = this.pointString[i * 3 + j];
    //         // this.pointString[i * 3 + j] * this.multiplier;
    //       }
    //       idx += 1;
    //     }
    //   }
    //   this.viewStore.filteredBlockIdString = filteredBlockIdStringTemp;
    //   this.viewStore.filteredPointString = filteredPointStringTemp;
    // },
    async updatePoints() {
      this.modelLoading = true;
      console.log("updatePoints")
      // if (this.radius < 0.01) {
      //   this.multiplier = (1 - this.radius / 0.5) * 30;
      //   this.radius=0.01
      // } else if (this.radius <= 0.2) {
      //   this.multiplier = (1 - this.radius / 0.5) * 30;
      // } else {
      //   this.multiplier = 1;
      // }
      // this.filterPointData();
      this.modelLoading = false;
    },
    async getPointDataAndUpdateDx() {

      console.log("getPointDataAndUpdateDx")
      let params = {
        model_name: this.modelData.model.modelNameSelected,
        model_folder_name: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        output: this.getPlotOutput,
        tasks: this.modelData.job.tasks,
        axis: this.modelParams.axis,
        step: this.modelParams.step,
        displ_factor: this.modelParams.displFactor,
        variable: this.modelParams.variable,
      }
      let data = null;
      await this.$api.get('/results/getPointData', { params })
        .then((response) => {
          data = response.data
          // this.$q.notify({
          //   message: "Test"
          // })
        })
        .catch(() => {
          this.$q.notify({
            type: 'negative',
            message: 'Results cannot be loaded',
          })
        })
      console.log(data)
      this.pointString = data["nodes"]
      this.blockIdString = data["value"]
      this.dx_value = Math.hypot(
        parseFloat(this.pointString[3]) - parseFloat(this.pointString[0]),
        parseFloat(this.pointString[4]) - parseFloat(this.pointString[1]),
        parseFloat(this.pointString[5]) - parseFloat(this.pointString[2])
      );
      this.maxValue = data["max_value"]
      this.minValue = data["min_value"]
      this.variableOptions = data["variables"]
      this.modelParams.numberOfSteps = data["number_of_steps"]
      this.time = data["time"]
    },
  },
  watch: {
    maxValue(newValue) {
      this.legendKey++; // Increment key to force re-rendering
    },
    minValue(newValue) {
      this.legendKey++; // Increment key to force re-rendering
    }
  }
}
</script>

<style>
.viewport {
  height: calc(100% - 50px);
  width: 100%;
}

.settings-column {
  width: 120px;
  margin-left: 5px;
  margin-top: 5px;
}

.legend {
  position: absolute;
  bottom: 160px;
  left: 20px;
  width: 100px;
}

.variables {
  position: absolute;
  top: 60px;
  left: 16px;
  width: 150px;
}

.variable {
  padding: 10px
}

.settings {
  height: 50px;
}
</style>
