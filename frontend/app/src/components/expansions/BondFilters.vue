<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="bondFilter, index in store.modelData.bondFilters" :key="bondFilter.bondFiltersId"
      style="padding: 0px">
      <div class="row my-row">
        <q-input class="my-input" v-model="bondFilter.name" :rules="[rules.required, rules.name]"
          :label="bondFilterKeys.name" standout dense></q-input>
        <q-select class="my-select" :options="bondFiltertype" v-model="bondFilter.type" :label="bondFilterKeys.type"
          standout dense></q-select>
        <q-input v-if="bondFilter.type == 'Rectangular_Plane'" class="my-input" v-model="bondFilter.bottomLength"
          :rules="[rules.required, rules.float]" :label="bondFilterKeys.bottomLength" standout dense></q-input>
        <q-input v-if="bondFilter.type == 'Rectangular_Plane'" class="my-input" v-model="bondFilter.sideLength"
          :rules="[rules.required, rules.float]" :label="bondFilterKeys.sideLength" standout dense></q-input>
        <q-input v-if="bondFilter.type == 'Disk'" class="my-input" v-model="bondFilter.radius"
          :rules="[rules.required, rules.float]" :label="bondFilterKeys.radius" standout dense></q-input>
        <q-toggle class="my-toggle" v-model="bondFilter.allow_contact" :label="bondFilterKeys.allow_contact" standout
          dense></q-toggle>
        <q-btn flat icon="fas fa-trash-alt" @click="removeBondFilter(index)">
          <q-tooltip>
            Remove Bond Filter
          </q-tooltip>
        </q-btn>
      </div>
      <div class="row my-row">
        <q-input class="my-input" v-model.number="bondFilter.normalX" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.normalX" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.normalY" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.normalY" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.normalZ" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.normalZ" standout dense></q-input>
        <q-toggle class="my-toggle" v-model="bondFilter.show" label="Show" standout dense></q-toggle>
      </div>
      <div class="row my-row" v-show="bondFilter.type == 'Rectangular_Plane'">
        <q-input class="my-input" v-model.number="bondFilter.lowerLeftCornerX" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.lowerLeftCornerX" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.lowerLeftCornerY" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.lowerLeftCornerY" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.lowerLeftCornerZ" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.lowerLeftCornerZ" standout dense></q-input>
      </div>
      <div class="row my-row" v-show="bondFilter.type == 'Rectangular_Plane'">
        <q-input class="my-input" v-model.number="bondFilter.bottomUnitVectorX" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.bottomUnitVectorX" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.bottomUnitVectorY" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.bottomUnitVectorY" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.bottomUnitVectorZ" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.bottomUnitVectorZ" standout dense></q-input>
      </div>
      <div class="row my-row" v-show="bondFilter.type == 'Disk'">
        <q-input class="my-input" v-model.number="bondFilter.centerX" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.centerX" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.centerY" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.centerY" standout dense></q-input>
        <q-input class="my-input" v-model.number="bondFilter.centerZ" :rules="[rules.required, rules.float]"
          :label="bondFilterKeys.centerZ" standout dense></q-input>
      </div>
      <q-separator></q-separator>
    </q-list>

    <q-btn flat icon="fas fa-plus" @click="addBondFilter">
      <q-tooltip>
        Add Bond Filter
      </q-tooltip>
    </q-btn>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import type { BondFilters } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'BondFilterSettings',
  setup() {
    const store = useModelStore();
    const viewStore = useViewStore();
    return {
      store,
      viewStore,
      rules
    }
  },
  created() {
    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
    this.$bus.on('showHideBondFilters', () => {
      this.showHideBondFilters()
    }),
      this.$bus.on('updateCracklength', () => {
        this.updateCracklength()
      })
  },
  data() {
    return {
      bondFiltertype: ['Rectangular_Plane', 'Disk'],
      bondFilterKeys: {
        name: 'name',
        type: 'Type',
        allow_contact: 'Allow Contact',
        normalX: 'Normal_X',
        normalY: 'Normal_Y',
        normalZ: 'Normal_Z',
        lowerLeftCornerX: 'Lower_Left_Corner_X',
        lowerLeftCornerY: 'Lower_Left_Corner_Y',
        lowerLeftCornerZ: 'Lower_Left_Corner_Z',
        bottomUnitVectorX: 'Bottom_Unit_Vector_X',
        bottomUnitVectorY: 'Bottom_Unit_Vector_Y',
        bottomUnitVectorZ: 'Bottom_Unit_Vector_Z',
        bottomLength: 'Bottom_Length',
        sideLength: 'Side_Length',
        centerX: 'Center_X',
        centerY: 'Center_Y',
        centerZ: 'Center_Z',
        radius: 'Radius',
      },
    };
  },
  methods: {
    updateCracklength() {
      if (this.store.selectedModel.file == 'CompactTension') {
        const cracklength = this.store.modelData.model.cracklength
        const length = this.store.modelData.model.length
        console.log(cracklength)
        console.log(length)
        const width = this.store.modelData.model.width
        this.store.modelData.bondFilters[0]!.bottomLength = +cracklength + 0.5 + 0.25 * +length
        if (this.store.modelData.model.twoDimensional) {
          this.store.modelData.bondFilters[0]!.sideLength = 2.0
          this.store.modelData.bondFilters[0]!.lowerLeftCornerZ = -1
        } else {
          this.store.modelData.bondFilters[0]!.sideLength = width + 2.0
          this.store.modelData.bondFilters[0]!.lowerLeftCornerZ = (-width / 2) - 1
        }
      }
    },
    addBondFilter() {
      const len = this.store.modelData.bondFilters.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.store.modelData.bondFilters[len - 1])) : {} as BondFilters;
      newItem.bondFilterId = len + 1
      newItem.name = 'bf_' + (len + 1)
      this.store.modelData.bondFilters.push(newItem);
      this.viewStore.bondFilterPoints.push({
        bondFilterPointsId: len + 1,
        bondFilterPointString: [],
      });
    },
    removeBondFilter(index) {
      this.store.modelData.bondFilters.splice(index, 1);
      this.viewStore.bondFilterPoints.splice(index, 1);
    },

    cross(a1: number, a2: number, a3: number, b1: number, b2: number, b3: number) {
      return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1];
    },
    vectorLength(a1: number, a2: number, a3: number) {
      return Math.sqrt(a1 * a1 + a2 * a2 + a3 * a3);
    },
    getVectorNorm(a1: number, a2: number, a3: number) {
      const bottomLength = Math.abs(this.vectorLength(a1, a2, a3));
      const normx = a1 / bottomLength;
      const normy = a2 / bottomLength;
      const normz = a3 / bottomLength;
      return [normx, normy, normz];
    },
    showHideBondFilters() {
      console.log('showHideBondFilters')
      // this.bondFilterPolyString = []
      // let bondFilterPolyString = []
      this.viewStore.bondFilterPoints = [];

      for (let i = 0; i < this.store.modelData.bondFilters.length; i++) {
        const bondFilterPointString = [];
        const bondFilter = this.store.modelData.bondFilters[i]!;
        if (bondFilter.show) {
          const nx = bondFilter.normalX;
          const ny = bondFilter.normalY;
          const nz = bondFilter.normalZ;

          if (bondFilter.type == 'Disk') {
            const cx = bondFilter.centerX;
            const cy = bondFilter.centerY;
            const cz = bondFilter.centerZ;
            const radius = bondFilter.radius;

            const crossVector1 = this.cross(nx, ny, nz, 1.0, 0.0, 0.0);
            const crossVector2 = this.cross(nx, ny, nz, 0.0, 1.0, 0.0);
            const crossVector3 = this.cross(nx, ny, nz, -1.0, 0.0, 0.0);
            const crossVector4 = this.cross(nx, ny, nz, 0.0, -1.0, 0.0);

            const normVector1 = this.getVectorNorm(
              crossVector1[0],
              crossVector1[1],
              crossVector1[2]
            );
            const normVector2 = this.getVectorNorm(
              crossVector2[0],
              crossVector2[1],
              crossVector2[2]
            );
            const normVector3 = this.getVectorNorm(
              crossVector3[0],
              crossVector3[1],
              crossVector3[2]
            );
            const normVector4 = this.getVectorNorm(
              crossVector4[0],
              crossVector4[1],
              crossVector4[2]
            );

            const point1x = cx + normVector1[0]! * radius;
            const point1y = cy + normVector1[1]! * radius;
            const point1z = cz + normVector1[2]! * radius;
            const point2x = cx + normVector2[0]! * radius;
            const point2y = cy + normVector2[1]! * radius;
            const point2z = cz + normVector2[2]! * radius;
            const point3x = cx + normVector3[0]! * radius;
            const point3y = cy + normVector3[1]! * radius;
            const point3z = cz + normVector3[2]! * radius;
            const point4x = cx + normVector4[0]! * radius;
            const point4y = cy + normVector4[1]! * radius;
            const point4z = cz + normVector4[2]! * radius;

            bondFilterPointString.push(point1x, point1y, point1z);
            bondFilterPointString.push(point2x, point2y, point2z);
            bondFilterPointString.push(point3x, point3y, point3z);
            bondFilterPointString.push(point4x, point4y, point4z);
          } else {
            const lx = bondFilter.lowerLeftCornerX;
            const ly = bondFilter.lowerLeftCornerY;
            const lz = -bondFilter.lowerLeftCornerZ!;
            const bx = bondFilter.bottomUnitVectorX;
            const by = bondFilter.bottomUnitVectorY;
            const bz = bondFilter.bottomUnitVectorZ;
            const bl = bondFilter.bottomLength;
            const sl = bondFilter.sideLength;

            const point1x = lx;
            const point1y = ly;
            const point1z = lz;

            const [normx, normy, normz] = this.getVectorNorm(bx, by, bz);

            const point2x = lx + normx! * bl;
            const point2y = ly + normy! * bl;
            const point2z = lz + normz! * bl;

            const crossVector = this.cross(nx, ny, nz, bx, by, bz);

            const normVector = this.getVectorNorm(
              crossVector[0],
              crossVector[1],
              crossVector[2]
            );

            const point4x = lx + normVector[0]! * sl;
            const point4y = ly + normVector[1]! * sl;
            const point4z = lz + normVector[2]! * sl;

            const point3x = point2x + normVector[0]! * sl;
            const point3y = point2y + normVector[1]! * sl;
            const point3z = point2z + normVector[2]! * sl;

            bondFilterPointString.push(point1x, point1y, point1z);
            bondFilterPointString.push(point2x, point2y, point2z);
            bondFilterPointString.push(point3x, point3y, point3z);
            bondFilterPointString.push(point4x, point4y, point4z);

            // bondFilterPolyString.push(4, 0, 1, 3, 2)
          }
        }
        if (this.viewStore.bondFilterPoints.length < i + 1) {
          this.viewStore.bondFilterPoints.push({
            bondFilterPointsId: i + 1,
            bondFilterPointString: [],
          });
        }
        this.viewStore.bondFilterPoints[i]!.bondFilterPointString = bondFilterPointString;

        // this.viewStore.bondFilterPoints[i].bondFilterPolyString = bondFilterPolyString
      }
    },
  },
  watch: {
    'store.modelData.bondFilters': {
      handler() {
        console.log('bondFilters changed!');
        this.showHideBondFilters();
      },
      deep: true,
    },
  }
})
</script>
