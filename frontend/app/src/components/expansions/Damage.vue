<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="damage, index in damages" :key="damage.damagesId" style="padding: 0px">
      <div
        v-bind:style="(damage.damagesId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
        <h4 class="my-title">Damage Model {{ damage.damagesId }}</h4>
        <div class="row my-row">
          <q-input class="my-input" v-model="damage.name" :rules="[rules.required, rules.name]" :label="damageKeys.name"
            standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeDamage(index)">
            <q-tooltip>
              Remove Damage Model
            </q-tooltip>
          </q-btn>
        </div>
        <div class="row my-row">
          <q-select class="my-input" :options="damageModelName" v-model="damage.damageModel"
            :label="damageKeys.damageModel" standout dense></q-select>
        </div>
        <div class="row my-row" v-if="damage.damageModel != 'Von Mises Stress'">
          <q-input class="my-input" v-model="damage.criticalStretch" :rules="[rules.required, rules.float]"
            :label="damageKeys.criticalStretch" clearable standout dense></q-input>
          <q-input class="my-input" v-model="damage.criticalEnergy" :rules="[rules.required, rules.float]"
            :label="damageKeys.criticalEnergy" clearable standout dense
            :readonly="damage.criticalEnergyCalc.calculateCriticalEnergy"></q-input>
        </div>
        <div class="row my-row" v-if="damage.damageModel == 'Von Mises Stress'">
          <q-input class="my-input" v-model="damage.criticalVonMisesStress" :rules="[rules.required, rules.float]"
            :label="damageKeys.criticalVonMisesStress" clearable standout dense></q-input>
          <q-input class="my-input" v-model="damage.criticalDamage" :rules="[rules.required, rules.float]"
            :label="damageKeys.criticalDamage" clearable standout dense></q-input>
        </div>
        <div class="row my-row" v-if="damage.damageModel == 'Von Mises Stress'">
          <q-input class="my-input" v-model="damage.thresholdDamage" :rules="[rules.required, rules.float]"
            :label="damageKeys.thresholdDamage" clearable standout dense></q-input>
          <q-input class="my-input" v-model="damage.criticalDamageToNeglect" :rules="[rules.required, rules.float]"
            :label="damageKeys.criticalDamageToNeglect" clearable standout dense></q-input>
        </div>
        <q-toggle class="my-toggle" v-model="damage.criticalEnergyCalc.calculateCriticalEnergy"
          label="Calculate Critical Energy" dense></q-toggle>
        <div class="row my-row" v-if="damage.criticalEnergyCalc.calculateCriticalEnergy">
          <q-input class="my-input" v-model="damage.criticalEnergyCalc.k1c" :rules="[rules.required, rules.float]"
            label="Fracture Toughness (K1C)" @update:model-value="calculateCriticalEnergy(index)" clearable standout
            dense></q-input>
        </div>
        <q-toggle class="my-toggle" v-model="damage.interBlockDamage" label="Inter Block Damage" dense></q-toggle>
        <div v-if="damage.interBlockDamage">
          <q-list v-for="prop, subindex in damage.interBlocks" :key="prop.damagesInterId" style="padding: 0px">
            <div class="row my-row">
              <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
                v-model="prop.firstBlockId" label="First Block Id" standout dense></q-select>
              <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
                v-model="prop.secondBlockId" label="Second Block Id" standout dense></q-select>
              <q-input class="my-input" v-model="prop.value" :rules="[rules.required, rules.float]"
                label="Critical Energ" standout dense></q-input>
              <q-btn flat icon="fas fa-trash-alt" @click="removeInterBlock(index, subindex)">
                <q-tooltip>
                  Remove InterBlock
                </q-tooltip>
              </q-btn>
            </div>
          </q-list>
          <div class="row my-row">
            <q-btn flat icon="fas fa-plus" @click="addInterBlock(index)">
              <q-tooltip>
                Add InterBlock
              </q-tooltip>
            </q-btn>
          </div>
        </div>
        <q-toggle class="my-toggle" v-model="damage.anistropicDamage" :label="damageKeys.anistropicDamage"
          dense></q-toggle>
        <div class="row my-row" v-if="damage.anistropicDamage">
          <q-input class="my-input" v-model="damage.anistropicDamageX" :rules="[rules.required, rules.float]"
            :label="damageKeys.anistropicDamageX" standout dense></q-input>
          <q-input class="my-input" v-model="damage.anistropicDamageY" :rules="[rules.required, rules.float]"
            :label="damageKeys.anistropicDamageY" standout dense></q-input>
          <q-input class="my-input" v-show="!store.modelData.model.twoDimensional" v-model="damage.anistropicDamageZ"
            :rules="[rules.required, rules.float]" :label="damageKeys.anistropicDamageZ" standout dense></q-input>
        </div>
        <q-toggle class="my-toggle" v-model="damage.onlyTension" :label="damageKeys.onlyTension" dense></q-toggle>
        <div class="row my-row">
          <q-select class="my-input" :options="stabilizationType" v-model="damage.stabilizationType"
            :label="damageKeys.stabilizationType" standout dense></q-select>
        </div>
        <q-toggle class="my-toggle" v-model="damage.detachedNodesCheck" :label="damageKeys.detachedNodesCheck"
          dense></q-toggle>
        <div class="row my-row">
          <q-input class="my-input" v-model="damage.thickness" :rules="[rules.required, rules.float]"
            :label="damageKeys.thickness" standout dense></q-input>
        </div>
        <div class="row my-row">
          <q-input class="my-input" v-model="damage.hourglassCoefficient" :rules="[rules.required, rules.float]"
            :label="damageKeys.hourglassCoefficient" standout dense></q-input>
        </div>
      </div>
      <q-separator></q-separator>
    </q-list>
    <q-btn flat icon="fas fa-plus" @click="addDamage">
      <q-tooltip>
        Add Damage Model
      </q-tooltip>
    </q-btn>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { inject } from 'vue'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'DamageSettings',
  setup() {
    const store = useModelStore();
    const damages = computed(() => store.modelData.damages)
    const blocks = computed(() => store.modelData.blocks)
    const materials = computed(() => store.modelData.materials)
    const bus = inject('bus')
    return {
      store,
      damages,
      blocks,
      materials,
      rules,
      bus
    }
  },
  created() {
  },
  data() {
    return {
      damageModelName: [
        'Critical Stretch',
        'Critical Energy',
      ],
      // damageModelName: [
      //   'Critical Stretch',
      //   'Von Mises Stress',
      //   'Interface Aware',
      //   'Time Dependent Critical Stretch',
      //   'Critical Energy',
      //   'Initial Damage',
      //   'Time Dependent Critical Stretch',
      //   'Critical Energy Correspondence',
      // ],
      damageKeys: {
        name: 'name',
        damageModel: 'Damage Model',
        criticalStretch: 'Critical Stretch',
        criticalEnergy: 'Critical Energy',
        criticalVonMisesStress: 'Critical Von Mises Stress',
        criticalDamage: 'Critical Damage',
        thresholdDamage: 'Threshold Damage',
        criticalDamageToNeglect: 'Critical Damage To Neglect Material Point',
        interBlockDamage: 'Interblock Damage',
        anistropicDamage: 'Anistropic Damage',
        anistropicDamageX: 'Anistropic Damage X',
        anistropicDamageY: 'Anistropic Damage Y',
        anistropicDamageZ: 'Anistropic Damage Z',
        numberOfBlocks: 'Number of Blocks',
        interBlockCriticalEnergy: 'Interblock Critical Energy',
        planeStress: 'Plane Stress',
        onlyTension: 'Only Tension',
        detachedNodesCheck: 'Detached Nodes Check',
        thickness: 'Thickness',
        hourglassCoefficient: 'Hourglass Coefficient',
        stabilizationType: 'Stabilization Type',
      },
      stabilizationType: [
        'Bond Based',
        'State Based',
        'Sub Horizon',
        'Global Stiffness',
      ],
    };
  },
  methods: {
    addDamage() {
      if (!this.damages) {
        this.damages = []
      }
      const len = this.damages.length;
      let newItem = {}
      if (len != 0) {
        newItem = structuredClone(this.damages[len - 1])
      } else {
        newItem = {
          'damagesId': 1,
          'name': 'Damage 1',
          'criticalEnergyCalc': {},
        }
      }
      newItem.damagesId = len + 1
      newItem.name = 'Damage' + (len + 1)
      this.damages.push(newItem);
    },
    removeDamage(index) {
      this.damages.splice(index, 1);
      if (this.damages.length == 0) {
        for (var i = 0; i < this.blocks.length; i++) {
          this.blocks[i].damageModel = '';
        }
      }
    },
    addInterBlock(index) {
      if (!this.damages[index].interBlocks) {
        this.damages[index].interBlocks = []
      }
      const len = this.damages[index].interBlocks.length;
      let newItem = {}
      if (len != 0) {
        newItem = structuredClone(this.damages[index].interBlocks[len - 1])
      } else {
        newItem = {
          'damagesInterId': 1,
          'firstBlockId': 1,
          'secondBlockId': 2,
          'value': 0.1
        }
      }
      newItem.damagesInterId = len + 1
      newItem.firtsId = 1
      newItem.secondId = len + 1
      this.damages[index].interBlocks.push(newItem);
    },
    removeInterBlock(index, subindex) {
      this.damages[index].interBlocks.splice(subindex, 1);
    },
    calculateCriticalEnergy(damageId) {
      if (this.damages[damageId].criticalEnergyCalc.calculateCriticalEnergy) {
        const k1c = this.damages[damageId].criticalEnergyCalc.k1c;
        if (k1c != null) {
          let E = null;
          let pr = null;
          let materialName = '';
          for (var i = 0; i < this.blocks.length; i++) {
            if (this.blocks[i].damageModel == this.damages[damageId].name) {
              materialName = this.blocks[i].material;
            }
          }
          let planeStress = true;
          for (var i = 0; i < this.materials.length; i++) {
            if (this.materials[i].name == materialName) {
              planeStress = this.materials[i].planeStress;
              E = this.materials[i].youngsModulus;
              pr = this.materials[i].poissonsRatio;
            }
          }
          if (planeStress) {
            this.damages[damageId].criticalEnergy = k1c ** 2 / +E;
          } else {
            this.damages[damageId].criticalEnergy =
              k1c ** 2 / (+E / (1 - pr ** 2));
          }
        }
      }
    },
  }
})
</script>
