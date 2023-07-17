<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h6">Typical Conversions</div>
      <div class="text-subtitle2">Enter constant to run the calculation</div>
    </q-card-section>

    <q-separator inset></q-separator>

    <q-card-section>
      <div class="row">
        <div class="col">
          <q-input 
              class="my-input"
              v-model="conversion.mass"
              label="Mass [kg]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.length"
              label="Length [m]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.velocity"
              label="Velocity [m/s]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.acceleration"
              label="Acceleration [m/s^2]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.moment"
              label="Moment [Nm]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.pressure"
              label="Pressure [Pa]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.density"
              label="Density [kg/m^3]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.energy"
              label="Energy [J]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.energyReleaseRate"
              label="Energy release rate [N/m]"
              clearable
              standout
              dense
          ></q-input>
          <q-input 
              class="my-input"
              v-model="conversion.fractureToughness"
              label="FractureToughness [MPa · m^1/2]"
              clearable
              standout
              dense
          ></q-input>
        </div>
        <div class="col">
          <q-input 
              class="my-input"
              v-model="conversionResults.mass"
              label="Mass [t]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('mass')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.length"
              label="Length [mm]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('length')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.velocity"
              label="Velocity [mm/s]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('velocity')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.acceleration"
              label="Acceleration [mm/s^2]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('acceleration')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.moment"
              label="Moment [Nmm]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('moment')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.pressure"
              label="Pressure [MPa]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('pressure')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.density"
              label="Density [t/mm^3]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('density')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.energy"
              label="Energy [mJ]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('energy')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.energyReleaseRate"
              label="Energy release rate [N/mm]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('energyReleaseRate')"></q-icon>
            </template>
          </q-input>
          <q-input 
              class="my-input"
              v-model="conversionResults.fractureToughness"
              label="Fracture Toughness [MPa · mm^1/2]"
              standout
              dense
          >
            <template v-slot:append>
              <q-icon name='fas fa-copy' @click="copyText('fractureToughness')"></q-icon>
            </template>
          </q-input>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
import { defineComponent } from 'vue'
import { copyToClipboard } from 'quasar'

export default defineComponent({
  name: 'SiConversionCard',
  data(){
    return{
      conversion: {
        mass: null,
        length: null,
        velocity: null,
        acceleration: null,
        moment: null,
        pressure: null,
        density: null,
        energy: null,
        energyReleaseRate: null,
        fractureToughness: null,
      },
      conversionResults:{
        mass: null,
        length: null,
        velocity: null,
        acceleration: null,
        moment: null,
        pressure: null,
        density: null,
        energy: null,
        energyReleaseRate: null,
        fractureToughnessm: null,
      },
    }
  },
  methods:{
    
    convertTypical() {
      const mass = this.conversion.mass;
      const length = this.conversion.length;
      const velocity = this.conversion.velocity;
      const acceleration = this.conversion.acceleration;
      const moment = this.conversion.moment;
      const pressure = this.conversion.pressure;
      const density = this.conversion.density;
      const energy = this.conversion.energy;
      const energyReleaseRate = this.conversion.energyReleaseRate;
      const fractureToughness = this.conversion.fractureToughness;

      if (mass != null) {
        this.conversionResults.mass = mass/1000;
      }
      if (length != null) {
        this.conversionResults.length = length*1000;
      }
      if (velocity != null) {
        this.conversionResults.velocity = velocity*1000;
      }
      if (acceleration != null) {
        this.conversionResults.acceleration = acceleration*1000;
      }
      if (moment != null) {
        this.conversionResults.moment = moment*1000;
      }
      if (pressure != null) {
        this.conversionResults.pressure = pressure/1000000;
      }
      if (density != null) {
        this.conversionResults.density = density/Math.pow(10, 12);
      }
      if (energy != null) {
        this.conversionResults.energy = energy*1000;
      }
      if (energyReleaseRate != null) {
        this.conversionResults.energyReleaseRate = energyReleaseRate/1000;
      }
      if (fractureToughness != null) {
        this.conversionResults.fractureToughness = Math.sqrt( fractureToughness **2 * 1000);
      }
    },
    copyText(id) {
      copyToClipboard(this.calculated[id])
    },
  },
  watch: {
    conversion: {
      handler() {
        console.log("conversion changed!");
        let num = 0;
        var con = [];
        for (con in this.conversion) {
          if (this.conversion[con] != null) {
            num++;
          }
        }
        if (num > 0) {
          this.convertTypical();
        }
        localStorage.setItem("conversion", JSON.stringify(this.conversion));
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