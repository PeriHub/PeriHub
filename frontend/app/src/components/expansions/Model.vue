<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-select class="my-select" :options="modelName" v-model="mod    el.modelNameSelected" v-show="    !model.ownModel"
      label="Model Name" standout dense></q-select>
    <q-input class="my-input" v-model="model.modelFolderName" label="Model Subname" placeholder="Default" standout
      dense></q-input>
    <q-input class="my-input" v-model="model.modelNameSelected" v-show="model.ownModel" :rules="[rules.required]"
      label="Model Name" standout dense></q-input>
    <q-input class="my-input" v-model="model.mesh    File" v-show="model.ownModel" :rules="[rules.required]"
      label="Mesh File" standout dense></q-input>
    <q-input class="my-input" v-model="model.length" v-show="!model.ownModel & model.mode    lNameSelected != 'RVE'"
      :rules="[rules.requ    ired, rules.float]" label="Length" standout dense></q-input>
    <q-input class="my-input" v-model="model.cracklen    gth"
      v-show="['GICmodel', 'GIICmodel', 'CompactTe    nsion'].includes(mode    l.modelNameSelected)"
      @update:model-value="bus.emit('upda    teCracklength')" :rules="[rules.required,     rules.float]" label="Cracklength"
      standout dense></q-input>
    <q-toggle class="my-toggle" v-model="model.notchEnabl    ed"
      v-show="['Compa    ctTension'].includes(model.modelNam    eSelected)" label="Notch enabled" dense></q-toggle>
    <q-input class="my-input" v-model="model.wid    th"
      v-show="!mo    del.ownModel &     model.modelNameSelected != '    RVE' & !model.twoDimensional"
      @update:model-value="bus.emit('updateCracklength'    )" :rules="[rules.requir    ed, rules.float]" label="Width" standout
      dense></q-input>
    <q-input class="my-input" v-model="model.height"
      v-show="!m    odel.ownModel & !['RVE', 'Com    pactTension', 'Smetana'].includes(mo    del.modelNameSelected)"
      :rules="[rules.required, rules.float]" label="Height" standout dense></q-input>
    <q-input class="my-input" v-model="mode    l.height"
      v-show="!model.ownMo    del & ['Smetana'].includes(mode    l.modelNameSelected)" :rules="[rules.requi    red, rules.float]"
      label="Ply height" standout dense></q-input>
    <q-input v-show="model.modelNa    meSelected == 'Dogbone' & !mo    del.ownModel" class="my-input" v-model="m    odel.height2"
      :rules="[rules.required,     rules.float]" label="Inner Height" standout dense></q-input>
    <q-input v-show="['PlateWithHole',     'RingOnRing'].includes(model.mod    elNameSelected) & !model.ownModel"
      class="my-input" v-model="model.radius" :rules="[rules.required, rules.float]" label="Radius" standout
      dense></q-input>
    <q-input v-show="model.modelNameSelected =    = 'RingOnRing' & !model.ownMode    l" class="my-input" v-model="model.radius2"
      :rules="[ru    les.required, rules.float]" label="Radius 2" standout dense></q-input>
    <q-input class="my-input" v-model="model.discretization" v-show="!model.ownModel & model.modelNameSelected != 'RVE'"
      :rules="[rules.required, rules.int]" label="Discretization" standout dense></q-input>
    <q-input class="my-input" v-model="model.horizon" v-show="model.ownModel" :rules="[rules.required, rul    es.posFloat]"
      label="Horizon" standout dense></q-input>
    <q-input class="my-input" v-model="model.amplitudeF    actor"
      v-show="!model.ow    nModel & model.modelNameSelected == 'Smetana'" :rules="[rules.required, rules.posFloat]"
      label="Amplitude Factor" standout dense></q-input>
    <q-input class="my-input" v-model="model.wavelength" v-show="!model.ownModel & model.modelNameSelected == 'Smetan    a'"
      :rules="[rules.required, rules.posFloat]" label="Wavelength" standout dense></q-input>
    <q-toggle class="my-toggle" v-show="model.modelNameSelected     == 'Dogbone' & !m    odel.ownMo    del"
      v-model="model.structured" label="Structured" dense></q-toggle>
    <q-toggle class="my-toggle" v-show="!model.ownModel & mo    del.modelNameSelected != 'RVE'"
      v-model="model.twoDimensional" label="Two Dimensional" dense></q-toggle>
    <q-toggle class="my-toggle" v-model="model.rotatedAngles"
      v-show="!model.ownModel & model.modelNameS    elected != 'RVE' & model.modelNameSelec    ted != 'Dogbone'"
      label="Rotated Angles" dense></q-toggle>
    <div class="row"
      v-show="model.rotatedAngles & !model.    ownModel & model.    modelNameS    elected != 'RVE' & model.modelNameSelected     != 'Dogbone'">
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
    </div>
    <!-- <div v-show="model.modelNameSelected=='RVE' & !model.ownModel">
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

<script>
import { computed, defineComponent, inject } from 'vue'
import { useModelStore } from 'stores/model-store';
import rules from "assets/rules.js";

export default defineComponent({
  name: 'ModelSettings',
  setup() {
    const store = useModelStore();
    const model = computed(() => store.modelData.model)
    const bus = inject('bus')
    let modelName = [
      "Dogbone",
      // "Kalthoff-Winkler",
      // "PlateWithOpening",
      // "PlateWithHole",
      // "ENFmodel",
      // "DCBmodel",
      "CompactTension",
      // "OwnModel",
      // "RingOnRing"
    ]
    if (process.env.DLR) {
      modelName.push("Smetana")
    }
    return {
      store,
      model,
      rules,
      bus,
      modelName
    }
  },
  created() {
    this.bus.on('resetData', () => {
      this.resetData()
    })
  },
  methods: {
    async resetData() {

      let route = '/assets/models/' + this.model.modelNameSelected + '/' + this.model.modelNameSelected + '.json';
      this.$api.get(route)
        .then((response) => {
          let jsonFile = response.data
          this.store.modelData = structuredClone(jsonFile)
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.data.detail
          })
        })
    },
  },
  watch: {
    'store.modelData.model.modelNameSelected': {
      handler() {
        console.log(this.store.modelData.model.modelNameSelected)
        if (!this.store.modelData.model.ownModel) {
          this.bus.emit("showModelImg", this.store.modelData.model.modelNameSelected)
          // this.resetData()
        }
        this.bus.emit("getStatus")
      },
    },
  }
})
</script>
