<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" standout dense v-model="model.ownModel" label="Own Model"
      @update:model-value="switchOwnModels" :disable="store.TRIAL"></q-toggle>
    <q-select class="my-select" :options="modelStore.availableModels" option-label="title"
      v-model="modelStore.selectedModel" v-show="!model.ownModel" label="Model Name" standout dense
      @update:model-value="selectMethod"></q-select>
    <q-input class="my-input" v-model="modelStore.selectedModel.file" v-show="model.ownModel" :rules="[rules.required]"
      label="Model Name" standout dense></q-input>

    <q-select standout dense class="q-pa-sm" v-model="model.modelFolderName" use-input hide-selected fill-input
      input-debounce="0" @new-value="createValue" :options="filteredModelFolderNameList" @filter="filterFn"
      label="Model Subname" @update:model-value="selectModelFolderName"></q-select>

    <!-- <q-input class="my-select" v-model="model.modelFolderName" label="Model Subname" placeholder="Default" standout
      dense></q-input> -->
    <q-input class="my-input" v-model="model.meshFile" v-show="model.ownModel" :rules="[rules.required]"
      label="Mesh File" standout dense></q-input>

    <q-toggle class="my-toggle" standout dense v-model="model.twoDimensional" label="Two Dimensional"></q-toggle>

    <div v-if="!model.ownModel">
      <div v-for="param in modelStore.modelParams.valves" :key="param.name">
        <!-- @vue-expect-error Bla-->
        <div v-if="!param.depends || modelStore.modelParams.valves.find(o => o.name === param.depends).value">
          <!-- @vue-expect-error Bla-->
          <q-input class="my-select" v-if="typeof(param.value) != 'boolean' && ['text', 'number'].includes(param.type)" :label="param.label"
            v-model="param.value" :type="param.type" standout dense>
            <q-tooltip>
              {{ param.description }}
            </q-tooltip>
          </q-input>
          <q-select class="my-select" standout dense v-if="param.type == 'select' && param.options" :options="param.options"
            option-label="name" v-model="param.value" :label="param.label">
            <q-tooltip>
              {{ param.description }}
            </q-tooltip>
          </q-select>
          <q-toggle class="my-toggle" standout dense v-if="param.type == 'checkbox'" v-model="param.value"
            :label="param.label">
            <q-tooltip>
              {{ param.description }}
            </q-tooltip>
          </q-toggle>
        </div>
      </div>
    </div>
    <!-- <q-input class="my-input" v-model="model.length" v-show="!model.ownModel & modelStore.selectedModel.file != 'RVE'"
      :rules="[rules.required, rules.float]" label="Length" standout dense></q-input>
    <q-input class="my-input" v-model="model.cracklength"
      v-show="['GICmodel', 'GIICmodel', 'CompactTension'].includes(modelStore.selectedModel.file)"
      @update:model-value="bus.emit('updateCracklength')" :rules="[rules.required, rules.float]" label="Cracklength"
      standout dense></q-input>
    <q-toggle class="my-toggle" v-model="model.notchEnabled"
      v-show="['CompactTension'].includes(modelStore.selectedModel.file)" label="Notch enabled" dense></q-toggle>
    <q-input class="my-input" v-model="model.width"
      v-show="!model.ownModel & modelStore.selectedModel.file != 'RVE' & !model.twoDimensional"
      @update:model-value="bus.emit('updateCracklength')" :rules="[rules.required, rules.float]" label="Width" standout
      dense></q-input>
    <q-input class="my-input" v-model="model.height"
      v-show="!model.ownModel & !['RVE', 'CompactTension', 'Smetana'].includes(modelStore.selectedModel.file)"
      :rules="[rules.required, rules.float]" label="Height" standout dense></q-input>
    <q-input class="my-input" v-model="model.height"
      v-show="!model.ownModel & ['Smetana'].includes(modelStore.selectedModel.file)" :rules="[rules.required, rules.float]"
      label="Ply height" standout dense></q-input>
    <q-input v-show="modelStore.selectedModel.file == 'Dogbone' & !model.ownModel" class="my-input" v-model="model.height2"
      :rules="[rules.required, rules.float]" label="Inner Height" standout dense></q-input>
    <q-input v-show="['PlateWithHole', 'RingOnRing'].includes(modelStore.selectedModel.file) & !model.ownModel"
      class="my-input" v-model="model.radius" :rules="[rules.required, rules.float]" label="Radius" standout
      dense></q-input>
    <q-input v-show="modelStore.selectedModel.file == 'RingOnRing' & !model.ownModel" class="my-input" v-model="model.radius2"
      :rules="[rules.required, rules.float]" label="Radius 2" standout dense></q-input>
    <q-input class="my-input" v-model="model.discretization" v-show="!model.ownModel & modelStore.selectedModel.file != 'RVE'"
      :rules="[rules.required, rules.int]" label="Discretization" standout dense></q-input>
    <q-input class="my-input" v-model="model.horizon" v-show="model.ownModel" :rules="[rules.required, rules.posFloat]"
      label="Horizon" standout dense></q-input>
    <q-input class="my-input" v-model="model.amplitudeFactor"
      v-show="!model.ownModel & modelStore.selectedModel.file == 'Smetana'" :rules="[rules.required, rules.posFloat]"
      label="Amplitude Factor" standout dense></q-input>
    <q-input class="my-input" v-model="model.wavelength" v-show="!model.ownModel & modelStore.selectedModel.file == 'Smetana'"
      :rules="[rules.required, rules.posFloat]" label="Wavelength" standout dense></q-input>
    <q-toggle class="my-toggle" v-show="modelStore.selectedModel.file == 'Dogbone' & !model.ownModel"
      v-model="model.structured" label="Structured" dense></q-toggle>
    <q-toggle class="my-toggle" v-show="!model.ownModel & modelStore.selectedModel.file != 'RVE'"
      v-model="model.twoDimensional" label="Two Dimensional" dense></q-toggle>
    <q-toggle class="my-toggle" v-model="model.rotatedAngles"
      v-show="!model.ownModel & modelStore.selectedModel.file != 'RVE' & modelStore.selectedModel.file != 'Dogbone'"
      label="Rotated Angles" dense></q-toggle>
    <div class="row"
      v-show="model.rotatedAngles & !model.ownModel & modelStore.selectedModel.file != 'RVE' & modelStore.selectedModel.file != 'Dogbone'">
      <div class="my-input">
        <q-input v-model="model.angles[0]" label="Angle 0" standout dense></q-input>
      </div>
      <div class="my-input">
        <q-input v-model="model.angles[1]" label="Angle 1" standout dense></q-input>
      </div>
      <div class="my-input">
        <q-input v-model="model.angles[2]" label="Angle 2" standout dense></q-input>
      </div>
      <div class="my-input">
        <q-input v-model="model.angles[3]" label="Angle 3" standout dense></q-input>
      </div>
    </div> -->
    <!-- <div v-show="modelStore.selectedModel.file=='RVE' & !model.ownModel">
                <v-text-field

                            class="my-input"
                    v-model="micofam.RVE.rve_fvc"
                    :rules="[rules.required, rules.float]"
                    label="rve_fvc"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.RVE.rve_radius"
                    :rules="[rules.required, rules.float]"
                    label="rve_radius"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.RVE.rve_lgth"
                    :rules="[rules.required, rules.float]"
                    label="rve_lgth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.RVE.rve_dpth"
                    :rules="[rules.required, rules.float]"
                    label="rve_dpth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.Mesh.mesh_fib"
                    :rules="[rules.required, rules.float]"
                    label="mesh_fib"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.Mesh.mesh_lgth"
                    :rules="[rules.required, rules.float]"
                    label="mesh_lgth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.Mesh.mesh_dpth"
                    :rules="[rules.required, rules.float]"
                    label="mesh_dpth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field

                            class="my-input"
                    v-model="micofam.Mesh.mesh_aa"
                    :rules="[rules.required]"
                    label="mesh_aa"
                    standout
                    dense
                ></v-text-field>
            </div> -->
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import { getModels, getValves, getJobFolders } from 'src/client'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'ModelSettings',
  setup() {
    const store = useDefaultStore();
    const modelStore = useModelStore();
    const model = computed(() => modelStore.modelData.model)
    return {
      store,
      modelStore,
      model,
      rules
    }
  },
  created() {
    this.$bus.on('getJobFolders', () => {
      this._getJobFolders()
    })
  },
  data() {
    return {
      modelFolderNameList: ['Default'],
      filteredModelFolderNameList: [] as string[],
    };
  },
  methods: {
    _getJobFolders() {
      getJobFolders({ modelName: this.modelStore.selectedModel.file }).then((response) => {
        this.modelFolderNameList = response
      })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.body.detail
          })
        })
    },
    async selectMethod() {
      // this.viewStore.viewLoading = true
      const response = await getValves({
        modelName: this.modelStore.selectedModel.file
      })
      this.modelStore.modelParams = response
      // this.viewStore.viewLoading = false
      this._getJobFolders()
    },
    selectModelFolderName() {
      this.$bus.emit('getStatus')
    },
    async switchOwnModels() {
      if (!this.model.ownModel) {
        this.modelStore.selectedModel = {
          title: 'Compact Tenison',
          file: 'CompactTension',
        }
      }
      await this.selectMethod()
    },
    createValue(val: string, done: (item: string, mode:  "add" | "add-unique" | "toggle" | undefined) => void) {

      if (val.length > 0) {
        if (!this.modelFolderNameList.includes(val)) {
          this.modelFolderNameList.push(val)
        }
        done(val, 'toggle')
      }
    },
    filterFn(val: string, update: (callbackFn: () => void) => void) {
      update(() => {
        if (val === '') {
          this.filteredModelFolderNameList = this.modelFolderNameList
        }
        else {
          const needle = val.toLowerCase()
          this.filteredModelFolderNameList = this.modelFolderNameList.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    }
  },
  async beforeMount() {
    this.modelStore.availableModels = await getModels()
    // this.selectMethod()
  },
  watch: {
    'modelStore.selectedModel': {
      handler() {
        localStorage.setItem('selectedModel', JSON.stringify(this.modelStore.selectedModel));
        if (!this.modelStore.modelData.model.ownModel) {
          this.$bus.emit('showModelImg', this.modelStore.selectedModel.file)
          // this.resetData()
        }
        this.$bus.emit('getStatus')
      },
      deep: true,
    },
  }
})
</script>
