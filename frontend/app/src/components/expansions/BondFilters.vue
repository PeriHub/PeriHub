<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

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
                    :rules="[rules.required, rules.name]" :label="bondFilterKeys.bottomLength" standout dense></q-input>
                <q-input v-if="bondFilter.type == 'Rectangular_Plane'" class="my-input" v-model="bondFilter.sideLength"
                    :rules="[rules.required, rules.name]" :label="bondFilterKeys.sideLength" standout dense></q-input>
                <q-input v-if="bondFilter.type == 'Disk'" class="my-input" v-model="bondFilter.radius"
                    :rules="[rules.required, rules.name]" :label="bondFilterKeys.radius" standout dense></q-input>
                <q-btn flat icon="fas fa-trash-alt" @click="removeBondFilter(index)">
                    <q-tooltip>
                        Remove Bond Filter
                    </q-tooltip>
                </q-btn>
            </div>
            <div class="row my-row">
                <q-input class="my-input" v-model="bondFilter.normalX" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.normalX" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.normalY" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.normalY" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.normalZ" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.normalZ" standout dense></q-input>
                <q-toggle class="my-toggle" v-model="bondFilter.show" label="Show" standout dense></q-toggle>
            </div>
            <div class="row my-row" v-show="bondFilter.type == 'Rectangular_Plane'">
                <q-input class="my-input" v-model="bondFilter.lowerLeftCornerX" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.lowerLeftCornerX" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.lowerLeftCornerY" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.lowerLeftCornerY" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.lowerLeftCornerZ" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.lowerLeftCornerZ" standout dense></q-input>
            </div>
            <div class="row my-row" v-show="bondFilter.type == 'Rectangular_Plane'">
                <q-input class="my-input" v-model="bondFilter.bottomUnitVectorX" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.bottomUnitVectorX" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.bottomUnitVectorY" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.bottomUnitVectorY" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.bottomUnitVectorZ" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.bottomUnitVectorZ" standout dense></q-input>
            </div>
            <div class="row my-row" v-show="bondFilter.type == 'Disk'">
                <q-input class="my-input" v-model="bondFilter.centerX" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.centerX" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.centerY" :rules="[rules.required, rules.float]"
                    :label="bondFilterKeys.centerY" standout dense></q-input>
                <q-input class="my-input" v-model="bondFilter.centerZ" :rules="[rules.required, rules.float]"
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
  
<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'stores/model-store';
import { useViewStore } from 'stores/view-store';
import { inject } from 'vue'
import rules from "assets/rules.js";

export default defineComponent({
    name: 'BondFilterSettings',
    setup() {
        const store = useModelStore();
        const viewStore = useViewStore();
        const bus = inject('bus')
        return {
            store,
            viewStore,
            rules,
            bus
        }
    },
    created() {
        this.bus.on('showHideBondFilters', () => {
            this.showHideBondFilters()
        }),
            this.bus.on('updateCracklength', () => {
                this.updateCracklength()
            })
    },
    data() {
        return {
            bondFiltertype: ["Rectangular_Plane", "Disk"],
            bondFilterKeys: {
                name: "name",
                type: "Type",
                normalX: "Normal_X",
                normalY: "Normal_Y",
                normalZ: "Normal_Z",
                lowerLeftCornerX: "Lower_Left_Corner_X",
                lowerLeftCornerY: "Lower_Left_Corner_Y",
                lowerLeftCornerZ: "Lower_Left_Corner_Z",
                bottomUnitVectorX: "Bottom_Unit_Vector_X",
                bottomUnitVectorY: "Bottom_Unit_Vector_Y",
                bottomUnitVectorZ: "Bottom_Unit_Vector_Z",
                bottomLength: "Bottom_Length",
                sideLength: "Side_Length",
                centerX: "Center_X",
                centerY: "Center_Y",
                centerZ: "Center_Z",
                radius: "Radius",
            },
        };
    },
    methods: {
        updateCracklength() {
            if (this.store.modelData.model.modelNameSelected == 'CompactTension') {
                const cracklength = this.store.modelData.model.cracklength
                const length = this.store.modelData.model.length
                console.log(cracklength)
                console.log(length)
                const width = this.store.modelData.model.width
                this.store.modelData.bondFilters[0].bottomLength = +cracklength + 0.5 + 0.25 * +length
                if (this.store.modelData.model.twoDimensional) {
                    this.store.modelData.bondFilters[0].sideLength = 2.0
                    this.store.modelData.bondFilters[0].lowerLeftCornerZ = -1
                } else {
                    this.store.modelData.bondFilters[0].sideLength = width + 2.0
                    this.store.modelData.bondFilters[0].lowerLeftCornerZ = (-width / 2) - 1
                }
            }
        },
        addBondFilter() {
            const len = this.store.modelData.bondFilters.length;
            let newItem = structuredClone(this.store.modelData.bondFilters[len - 1])
            newItem.bondFilterId = len + 1
            newItem.name = "bf_" + (len + 1)
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

        cross(a1, a2, a3, b1, b2, b3) {
            return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1];
        },
        vectorLength(a1, a2, a3) {
            return Math.sqrt(a1 * a1 + a2 * a2 + a3 * a3);
        },
        getVectorNorm(a1, a2, a3) {
            const bottomLength = Math.abs(this.vectorLength(a1, a2, a3));
            const normx = a1 / bottomLength;
            const normy = a2 / bottomLength;
            const normz = a3 / bottomLength;
            return [normx, normy, normz];
        },
        showHideBondFilters() {
            console.log("showHideBondFilters")
            // this.bondFilterPolyString = []
            // let bondFilterPolyString = []
            this.viewStore.bondFilterPoints = [];

            for (var i = 0; i < this.store.modelData.bondFilters.length; i++) {
                let bondFilterPointString = [];
                const bondFilter = this.store.modelData.bondFilters[i];
                if (bondFilter.show) {
                    const nx = parseFloat(bondFilter.normalX);
                    const ny = parseFloat(bondFilter.normalY);
                    const nz = parseFloat(bondFilter.normalZ);

                    if (bondFilter.type == "Disk") {
                        const cx = parseFloat(bondFilter.centerX);
                        const cy = parseFloat(bondFilter.centerY);
                        const cz = parseFloat(bondFilter.centerZ);
                        const radius = parseFloat(bondFilter.radius);

                        let crossVector1 = this.cross(nx, ny, nz, 1.0, 0.0, 0.0);
                        let crossVector2 = this.cross(nx, ny, nz, 0.0, 1.0, 0.0);
                        let crossVector3 = this.cross(nx, ny, nz, -1.0, 0.0, 0.0);
                        let crossVector4 = this.cross(nx, ny, nz, 0.0, -1.0, 0.0);

                        let normVector1 = this.getVectorNorm(
                            crossVector1[0],
                            crossVector1[1],
                            crossVector1[2]
                        );
                        let normVector2 = this.getVectorNorm(
                            crossVector2[0],
                            crossVector2[1],
                            crossVector2[2]
                        );
                        let normVector3 = this.getVectorNorm(
                            crossVector3[0],
                            crossVector3[1],
                            crossVector3[2]
                        );
                        let normVector4 = this.getVectorNorm(
                            crossVector4[0],
                            crossVector4[1],
                            crossVector4[2]
                        );

                        const point1x = cx + normVector1[0] * radius;
                        const point1y = cy + normVector1[1] * radius;
                        const point1z = cz + normVector1[2] * radius;
                        const point2x = cx + normVector2[0] * radius;
                        const point2y = cy + normVector2[1] * radius;
                        const point2z = cz + normVector2[2] * radius;
                        const point3x = cx + normVector3[0] * radius;
                        const point3y = cy + normVector3[1] * radius;
                        const point3z = cz + normVector3[2] * radius;
                        const point4x = cx + normVector4[0] * radius;
                        const point4y = cy + normVector4[1] * radius;
                        const point4z = cz + normVector4[2] * radius;

                        bondFilterPointString.push(point1x, point1y, point1z);
                        bondFilterPointString.push(point2x, point2y, point2z);
                        bondFilterPointString.push(point3x, point3y, point3z);
                        bondFilterPointString.push(point4x, point4y, point4z);
                    } else {
                        const lx = parseFloat(bondFilter.lowerLeftCornerX);
                        const ly = parseFloat(bondFilter.lowerLeftCornerY);
                        const lz = -parseFloat(bondFilter.lowerLeftCornerZ);
                        const bx = parseFloat(bondFilter.bottomUnitVectorX);
                        const by = parseFloat(bondFilter.bottomUnitVectorY);
                        const bz = parseFloat(bondFilter.bottomUnitVectorZ);
                        const bl = parseFloat(bondFilter.bottomLength);
                        const sl = parseFloat(bondFilter.sideLength);

                        const point1x = lx;
                        const point1y = ly;
                        const point1z = lz;

                        let [normx, normy, normz] = this.getVectorNorm(bx, by, bz);

                        const point2x = lx + normx * bl;
                        const point2y = ly + normy * bl;
                        const point2z = lz + normz * bl;

                        let crossVector = this.cross(nx, ny, nz, bx, by, bz);

                        let normVector = this.getVectorNorm(
                            crossVector[0],
                            crossVector[1],
                            crossVector[2]
                        );

                        const point4x = lx + normVector[0] * sl;
                        const point4y = ly + normVector[1] * sl;
                        const point4z = lz + normVector[2] * sl;

                        const point3x = point2x + normVector[0] * sl;
                        const point3y = point2y + normVector[1] * sl;
                        const point3z = point2z + normVector[2] * sl;

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
                this.viewStore.bondFilterPoints[i].bondFilterPointString = bondFilterPointString;

                // this.viewStore.bondFilterPoints[i].bondFilterPolyString = bondFilterPolyString
            }
        },
    },
    watch: {
        'store.modelData.bondFilters': {
            handler() {
                console.log("bondFilters changed!");
                this.showHideBondFilters();
            },
            deep: true,
        },
    }
})
</script>