<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div style="height: 100%; width: 100%; overflow: hidden">
    <div style="height:100%;">
      <div class="row" :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'">
        <q-btn padding="none" flat dense icon="fas fa-sync-alt" @click="viewPointData(true)">
          <q-tooltip>
            Reload Model
          </q-tooltip>
        </q-btn>
        <q-btn padding="none" flat dense icon="fas fa-expand" @click="$refs.view.resetCamera()">
          <q-tooltip>
            Reset Camera
          </q-tooltip>
        </q-btn>
        <q-btn :disabled="modelParams.step == 1" padding="none" flat dense icon="fas fa-fast-backward"
          @click="fastBackward()">
          <q-tooltip>
            Fast Backward
          </q-tooltip>
        </q-btn>
        <q-btn padding="none" flat dense icon="fas fa-backward" @click="backward()">
          <q-tooltip>
            Backward
          </q-tooltip>
        </q-btn>
        <q-btn :disabled="!playing" padding="none" flat dense icon="fas fa-pause" @click="pause()">
          <q-tooltip>
            Pause
          </q-tooltip>
        </q-btn>
        <q-btn :disabled="playing" padding="none" flat dense icon="fas fa-play" @click="play()">
          <q-tooltip>
            Play
          </q-tooltip>
        </q-btn>
        <q-btn padding="none" flat dense icon="fas fa-forward" @click="forward()">
          <q-tooltip>
            Forward
          </q-tooltip>
        </q-btn>
        <q-btn :disabled="modelParams.step == modelParams.numberOfSteps" padding="none" flat dense
          icon="fas fa-fast-forward" @click="fastForward()">
          <q-tooltip>
            Fast Forward
          </q-tooltip>
        </q-btn>
        <q-item style="padding-right: 5px">
          <q-item-section style="width: 10px; margin-right:15px" side>
            <q-icon color=" #cfcfcf" name="fas fa-clock" />
          </q-item-section>
          <q-item-section v-if="modelParams.numberOfSteps > 0">
            <q-slider style="width: 100px" v-model="modelParams.step" :min="0" :max="modelParams.numberOfSteps"
              :step="1" label :label-value="'Time Step: ' + modelParams.step" switch-label-side color="secondary"
              @change="viewPointData(true)"></q-slider>
          </q-item-section>
          <q-item-section side>
            {{ time }}
          </q-item-section>
        </q-item>
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
        <q-item style="padding-right: 5px">
          <q-item-section style="width: 10px; margin-right:15px" side>
            <q-icon color="#cfcfcf" name="fas fa-up-right-and-down-left-from-center" />
          </q-item-section>
          <q-item-section>
            <q-slider style="width: 80px" v-model="multiplier" :min="1" :max="200" :step="1" label
              :label-value="'Node Size: ' + multiplier + ' %'" switch-label-side @change="updatePoints"
              color="secondary"></q-slider>
          </q-item-section>
        </q-item>
        <q-item style="padding-right: 5px">
          <q-item-section style="width: 10px; margin-right:15px" side>
            <q-icon color="#cfcfcf" name="fas fa-eye" />
          </q-item-section>
          <q-item-section>
            <q-slider style="width: 80px" v-model="resolution" :min="3" :max="20" :step="1" label
              :label-value="'Resolution: ' + resolution" switch-label-side color="secondary"></q-slider>
          </q-item-section>
        </q-item>
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
        dense @update:model-value="viewPointData(true)"></q-select>
      <q-select class="variable" :options="axisOptions" v-model="modelParams.axis" label="Axis" outlined dense
        @update:model-value="viewPointData(true)"></q-select>
      <q-input class="variable" v-model.number="modelParams.displFactor" type="number" label="Displ. Magnitude" outlined
        dense debounce:500 @update:model-value="viewPointData(true)"></q-input>
      <q-expansion-item v-model="expansion" expand-separator dense dense-toggle icon="fas fa-cogs" label="Options">
        <q-select class="variable" :options="filterOptions" v-model="modelParams.filter" label="Filter" outlined dense
          clearable @update:model-value="viewPointData(true)"></q-select>
        <q-input class="variable" v-model.number="modelParams.colorBarMin" type="number" label="Min." outlined dense
          clearable debounce:500 @update:model-value="viewPointData(true)"></q-input>
        <q-input class="variable" v-model.number="modelParams.colorBarMax" type="number" label="Max." outlined dense
          clearable debounce:500 @update:model-value="viewPointData(true)"></q-input>
      </q-expansion-item>
    </div>
    <vertical-colored-legend class="legend" :min="minValue" :max="maxValue" :key="legendKey" />
    <q-inner-loading :showing="modelLoading">
      <q-spinner-gears size="50px" color="primary"></q-spinner-gears>
    </q-inner-loading>
  </div>
</template>

<script lang="ts">
import { computed } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import VerticalColoredLegend from 'src/components/tools/VerticalColoredLegend.vue';
import { getPointDataResults } from 'src/client';
export default {
  name: 'PeriLab_Web_Results',
  components: {
    VerticalColoredLegend
  },
  setup() {
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)

    return {
      modelData,
      modelStore
    }
  },
  data() {
    return {
      modelParams: {
        variable: 'Displacements',
        axis: 'Magnitude',
        displFactor: 1,
        step: 1,
        numberOfSteps: 100,
        filter: '',
        output: 'Output1',
        colorBarMin: null,
        colorBarMax: null
      },
      variableOptions: [
        'Displacements',
        'Damage',
        'Forces',
        'Temperature'
      ],
      axisOptions: [
        'X',
        'Y',
        'Z',
        'Magnitude'
      ],
      filterOptions: [
        'Active',
        'Temperature',
        'Displacements',
        'Damage',
      ],
      sphere: 'Sphere',
      resolution: 6,
      radius: 0.2,
      dx_value: 0.2,
      multiplier: 100,
      pointString: [1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 0, 9, 0, 0, 10, 0, 0, 11, 0, 0],
      blockIdString: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
      file: 'DCBmodel_Output1.e',
      modelLoading: false,
      drawer: false,
      maxValue: 100,
      minValue: 0,
      legendKey: 0,
      time: 0,
      playing: false,
      timer: NodeJS.Timeout,
      expansion: false
    };
  },

  mounted() {
    console.log('ModelView mounted')
    this.viewPointData(true);
    this.$refs.view.resetCamera();
  },
  methods: {
    async viewPointData(loading = true) {
      console.log('viewPointData')
      this.modelLoading = loading;

      await this.getPointDataAndUpdateDx();
      this.radius = parseFloat(this.dx_value.toFixed(3));
      this.updatePoints();

      this.modelLoading = false;
    },
    // filterPointData() {
    //   console.log('filterPointData')
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
    updatePoints() {
      this.modelLoading = true;
      console.log('updatePoints')
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

      console.log('getPointDataAndUpdateDx')
      await getPointDataResults({
        modelName: this.modelStore.selectedModel.file,
        modelFolderName: this.modelData.model.modelFolderName,
        cluster: this.modelData.job.cluster,
        output: this.modelData.outputs[0]!.name,
        tasks: this.modelData.job.tasks,
        axis: this.modelParams.axis,
        step: this.modelParams.step,
        displFactor: this.modelParams.displFactor,
        variable: this.modelParams.variable,
        filter: this.modelParams.filter,
        colorBarMin: Number(this.modelParams.colorBarMin),
        colorBarMax: Number(this.modelParams.colorBarMax)
      })
        .then((response) => {
          const data = response
          if (response.data == false) {
            this.$q.notify({
              type: 'negative',
              message: response.message,
            })
          } else {
            this.pointString = data['nodes']
            this.blockIdString = data['value']
            this.dx_value = Math.hypot(
              this.pointString[3]! - this.pointString[0]!,
              this.pointString[4]! - this.pointString[1]!,
              this.pointString[5]! - this.pointString[2]!
            );
            this.maxValue = data['max_value']
            this.minValue = data['min_value']
            this.variableOptions = data['variables']
            this.modelParams.numberOfSteps = data['number_of_steps']
            this.time = data['time']
          }
        })
        .catch((error) => {
          console.log(error)
          this.$q.notify({
            type: 'negative',
            message: error.response.detail,
          })
        })
    },
    play() {
      this.playing = true
      // eslint-disable @typescript-eslint/no-misused-promises
      // eslint-disable-next-line @typescript-eslint/unbound-method
      this.timer = setInterval(this.forward, 1000)
    },
    pause() {
      this.playing = false
      clearInterval(this.timer)
    },
    async backward() {
      if (this.modelParams.step > 1) {
        this.modelParams.step = this.modelParams.step - 1
        await this.viewPointData(false)
      }
    },
    async fastBackward() {
      this.modelParams.step = 1
      await this.viewPointData(false)
    },
    async forward() {
      if (this.modelParams.step < this.modelParams.numberOfSteps) {
        this.modelParams.step = this.modelParams.step + 1
        await this.viewPointData(false)
      } else {
        this.pause()
      }
    },
    async fastForward() {
      this.modelParams.step = this.modelParams.numberOfSteps
      await this.viewPointData(false)
    }

  },
  watch: {
    maxValue() {
      this.legendKey++; // Increment key to force re-rendering
    },
    minValue() {
      this.legendKey++; // Increment key to force re-rendering
    }
  },
  unmounted() {
    clearInterval(this.timer)
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
  top: 58px;
  left: 10px;
  width: 150px;
}

.variable {
  padding: 10px
}

.settings {
  height: 50px;
}
</style>
