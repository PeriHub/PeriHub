<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h6">Conversion of elastic isotropic constants</div>
      <div class="text-subtitle2">Enter two constants to run the calculations</div>
    </q-card-section>

    <q-separator inset></q-separator>

    <q-card-section>
      <div class="row">
        <div class="col">
          <q-input class="my-input" v-model="constants.E1" :label="materialKeys.E1" clearable standout dense></q-input>
          <q-input class="my-input" v-model="constants.E2" :label="materialKeys.E2" clearable standout dense></q-input>
          <q-input class="my-input" v-model="constants.E3" :label="materialKeys.E3" clearable standout dense></q-input>
          <q-input class="my-input" v-model="constants.G12" :label="materialKeys.G12" clearable standout
            dense></q-input>
          <q-input class="my-input" v-model="constants.G13" :label="materialKeys.G13" clearable standout
            dense></q-input>
          <q-input class="my-input" v-model="constants.G23" :label="materialKeys.G23" clearable standout
            dense></q-input>
          <q-input class="my-input" v-model="constants.nu12" :label="materialKeys.nu12" clearable standout
            dense></q-input>
          <q-input class="my-input" v-model="constants.nu13" :label="materialKeys.nu13" clearable standout
            dense></q-input>
          <q-input class="my-input" v-model="constants.nu23" :label="materialKeys.nu23" clearable standout
            dense></q-input>
        </div>
        <div class="col">
          <q-input class="my-input" v-model="calculated.C11" :label="materialKeys.C11" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C11')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.C12" :label="materialKeys.C12" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C12')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.C13" :label="materialKeys.C13" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C13')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.C14" :label="materialKeys.C14" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C14')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.C15" :label="materialKeys.C15" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C15')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.C16" :label="materialKeys.C16" standout dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('C16')"></q-icon>
            </template>
          </q-input>
          <q-input class="my-input" v-model="calculated.stiffnessString" :label="materialKeys.stiffnessString" standout
            dense>
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('stiffnessString')"></q-icon>
            </template>
          </q-input>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { copyToClipboard } from 'quasar'

export default defineComponent({
  name: 'StiffnesssCard',
  data() {
    return {
      constants: {
        E1: null as number | null,
        E2: null as number | null,
        E3: null as number | null,
        G12: null as number | null,
        G13: null as number | null,
        G23: null as number | null,
        nu12: null as number | null,
        nu13: null as number | null,
        nu23: null as number | null,
      },
      calculated: {
        C11: null as number | null,
        C12: null as number | null,
        C13: null as number | null,
        C14: null as number | null,
        C15: null as number | null,
        C16: null as number | null,
        C22: null as number | null,
        C23: null as number | null,
        C24: null as number | null,
        C25: null as number | null,
        C26: null as number | null,
        C33: null as number | null,
        C34: null as number | null,
        C35: null as number | null,
        C36: null as number | null,
        C44: null as number | null,
        C45: null as number | null,
        C46: null as number | null,
        C55: null as number | null,
        C56: null as number | null,
        C66: null as number | null,
        stiffnessString: '',
      },
      materialKeys: {
        E1: 'E1',
        E2: 'E2',
        E3: 'E3',
        G12: 'G12',
        G13: 'G13',
        G23: 'G23',
        nu12: 'nu12',
        nu13: 'nu13',
        nu23: 'nu23',
        C11: 'C11',
        C12: 'C12',
        C13: 'C13',
        C14: 'C14',
        C15: 'C15',
        C16: 'C16',
        stiffnessString: 'String'
      },
    }
  },
  methods: {
    convert() {
      const E1: number = this.constants.E1!;   // Elastic modulus along the fiber direction (Pa)
      const E2: number = this.constants.E2!;    // Elastic modulus transverse to the fiber direction (Pa)
      const E3: number = this.constants.E3!;    // Elastic modulus transverse to the fiber direction (Pa)
      const G12: number = this.constants.G12!;    // Shear modulus in the 1-2 plane (Pa)
      const G13: number = this.constants.G13!;    // Shear modulus in the 1-3 plane (Pa)
      const G23: number = this.constants.G23!;    // Shear modulus in the 2-3 plane (Pa)
      const nu12: number = this.constants.nu12!;   // Poisson's ratio in the 1-2 plane
      const nu13: number = this.constants.nu13!;   // Poisson's ratio in the 1-3 plane
      const nu23: number = this.constants.nu23!;   // Poisson's ratio in the 2-3 plane
      this.calculated.C11 = 1 / +E1;
      this.calculated.C22 = 1 / +E2;
      this.calculated.C33 = 1 / +E3;
      this.calculated.C12 = +nu12 / +E1;
      this.calculated.C13 = +nu13 / +E1;
      this.calculated.C23 = +nu23 / +E2;
      this.calculated.C44 = 1 / +G12;
      this.calculated.C55 = 1 / +G13;
      this.calculated.C66 = 1 / +G23;
      this.calculated.C46 = (1 - +nu12) / +E1;
      this.calculated.C36 = (1 - +nu13) / +E1;
      this.calculated.C26 = (1 - +nu23) / +E2;

      this.calculated.C14 = this.calculated.C15 = this.calculated.C24 = +nu12 / +E2;
      this.calculated.C25 = this.calculated.C34 = this.calculated.C16 = +nu13 / +E3;
      this.calculated.C35 = this.calculated.C26 = this.calculated.C45 = +nu23 / +E3;

      this.calculated.C56 = (1 - +nu12 - +nu23) / +E3;

      const stiffnessMatrix = [
        [this.calculated.C11, this.calculated.C12, this.calculated.C13, this.calculated.C14, this.calculated.C15, this.calculated.C16],
        [this.calculated.C22, this.calculated.C23, this.calculated.C24, this.calculated.C25, this.calculated.C26],
        [this.calculated.C33, this.calculated.C34, this.calculated.C35, this.calculated.C36],
        [this.calculated.C44, this.calculated.C45, this.calculated.C46],
        [this.calculated.C55, this.calculated.C56],
        [this.calculated.C66],
      ];
      const names = [['C11', 'C12', 'C13', 'C14', 'C15', 'C16'],
      ['C22', 'C23', 'C24', 'C25', 'C26'],
      ['C33', 'C34', 'C35', 'C36'],
      ['C44', 'C45', 'C46'],
      ['C55', 'C56'],
      ['C66']];

      this.calculated.stiffnessString = ''
      for (let i = 0; i < names.length; i++) {
        for (let j = 0; j < names[i]!.length; j++) {
          this.calculated.stiffnessString += names[i]![j] + ': ' + stiffnessMatrix[i]![j].toFixed(4) + '\n';
        }
      }
      // this.calculated.bulkModulus = Number(
      //   this.calculated.bulkModulus
      // ).toExponential();
      // this.calculated.youngsModulus = Number(
      //   this.calculated.youngsModulus
      // ).toExponential();
      // this.calculated.lameFirst = Number(
      //   this.calculated.lameFirst
      // ).toExponential();
      // this.calculated.shearModulus = Number(
      //   this.calculated.shearModulus
      // ).toExponential();
      // this.calculated.pWaveModulus = Number(
      //   this.calculated.pWaveModulus
      // ).toExponential();
    },
    resetResult() {
      this.calculated.C11 = null;
      this.calculated.C12 = null;
      this.calculated.C13 = null;
      this.calculated.C14 = null;
      this.calculated.C15 = null;
      this.calculated.C16 = null;
      this.calculated.C22 = null;
      this.calculated.C23 = null;
      this.calculated.C24 = null;
      this.calculated.C25 = null;
      this.calculated.C26 = null;
      this.calculated.C33 = null;
      this.calculated.C34 = null;
      this.calculated.C35 = null;
      this.calculated.C36 = null;
      this.calculated.C44 = null;
      this.calculated.C45 = null;
      this.calculated.C46 = null;
      this.calculated.C55 = null;
      this.calculated.C56 = null;
      this.calculated.C66 = null;
    },
    copyText(id) {
      copyToClipboard(this.calculated[id]!)
        .then(() => {
          this.$q.notify({
            message: 'Copied to clipboard',
          })
        }).catch(() => {
          this.$q.notify({
            message: 'Failed to copy',
          })
        });
    },
  },
  mounted() {
    if (localStorage.getItem('constants')) {
      const object = JSON.parse(localStorage.getItem('constants')!)
      this.constants = structuredClone(object)
    }
  },
  watch: {
    constants: {
      handler() {
        console.log('constants changed!');
        let num = 0;
        let con = [];
        for (con in this.constants) {
          if (this.constants[con] != null) {
            num++;
          }
        }
        if (num == 9) {
          this.convert();
        }
        if (num != 9) {
          this.resetResult();
        }
        localStorage.setItem('constants', JSON.stringify(this.constants));
      },
      deep: true,
    },
  }
})
</script>
<style scoped>
.my-input {
  margin-left: 10px;
}
</style>
