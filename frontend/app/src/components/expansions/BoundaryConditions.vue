<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div>
            <q-list
                v-for="nodeSet in boundaryConditions.nodeSets"
                :key="nodeSet.nodeSetId"
                style="padding: 0px"
            >
                <div class="row my-row">
                    <q-input 
                        class="my-input"
                        v-model="nodeSet.file"
                        :rules="[rules.required, rules.name]"
                        label="Nodeset"
                        standout
                        dense
                    ></q-input>
                </div>
                <q-separator></q-separator>
            </q-list>
            <q-list
                v-for="boundaryCondition, index in boundaryConditions.conditions"
                :key="boundaryCondition.conditionsId"
                style="padding: 0px"
            >
                <div class="row my-row">
                    <q-input 
                        class="my-input"
                        v-model="boundaryCondition.name"
                        :rules="[rules.required, rules.name]"
                        :label="boundaryKeys.name"
                        standout
                        dense
                    ></q-input>
                    <q-select 
                        class="my-select"
                        :options="boundarytype"
                        v-model="boundaryCondition.boundarytype"
                        :label="boundaryKeys.boundarytype"
                        standout
                        dense
                    ></q-select>
                    <q-input 
                        class="my-input"
                        v-model="boundaryCondition.nodeSet"
                        :rules="[rules.required, rules.name]"
                        :label="boundaryKeys.nodeSet"
                        standout
                        dense
                    ></q-input>
                </div> 
                <div class="row my-row">
                    <q-select 
                        v-show="!model.ownModel"
                        class="my-input"
                        :options="blocks"
                        option-label="blocksId"
                        option-value="blocksId"
                        emit-value
                        v-model="boundaryCondition.blockId"
                        :label="boundaryKeys.blockId"
                        clearable
                        standout
                        dense
                    ></q-select>
                    <q-select 
                        class="my-select"
                        :options="coordinate"
                        v-model="boundaryCondition.coordinate"
                        :label="boundaryKeys.coordinate"
                        clearable
                        standout
                        dense
                    ></q-select>
                    <q-input 
                        class="my-input"
                        v-model="boundaryCondition.value"
                        :rules="[rules.required, rules.name]"
                        :label="boundaryKeys.value"
                        standout
                        dense
                    ></q-input>
                    <q-btn flat icon="fas fa-trash-alt" @click="removeCondition(index)">
                        <q-tooltip>
                            Remove Condition
                        </q-tooltip>
                    </q-btn>
                </div>
                <q-separator></q-separator>
            </q-list>
            
            <q-btn flat icon="fas fa-plus" @click="addCondition">
                <q-tooltip>
                    Add Condition
                </q-tooltip>
            </q-btn>
        </div>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
    import { deepCopy } from '../../utils/functions.js'
  
    export default defineComponent({
        name: 'BoundaryConditionsSettings',
        setup() {
            const store = useModelStore();
            const model = computed(() => store.modelData.model)
            const blocks = computed(() => store.modelData.blocks)
            const boundaryConditions = computed(() => store.modelData.boundaryConditions)
            const bus = inject('bus')
            return {
                store,
                model,
                blocks,
                boundaryConditions,
                rules,
                bus
            }
        },
        created() {
        },
        data() {
            return {
                boundarytype: [
                    "Initial Displacement",
                    "Initial Velocity",
                    "Prescribed Displacement",
                    "Prescribed Fluid Pressure U",
                    "Initial Fluid Pressure U",
                    "Initial Temperature",
                    "Prescribed Temperature",
                    "Thermal Flux",
                    "Body Force",
                ],
                coordinate: ["x", "y", "z"],
                boundaryKeys: {
                    name: "name",
                    nodeSet: "Node Set",
                    boundarytype: "Type",
                    blockId: "Block Id",
                    coordinate: "Coordinate",
                    value: "Value",
                },
            };
        },
        methods: {
            addCondition() {
                const len = this.boundaryConditions.conditions.length;
                let newItem = deepCopy(this.boundaryConditions.conditions[len - 1])
                newItem.boundaryConditionsId = len + 1
                newItem.name = "BC_" + (len + 1)
                this.boundaryConditions.conditions.push(newItem);
                this.boundaryConditions.nodeSets.push({
                    nodeSetId: len + 1,
                    file: "ns_bc" + len,
                });
            },
            removeCondition(index) {
                this.boundaryConditions.conditions.splice(index, 1);
                this.boundaryConditions.nodeSets.splice(index, 1);
            },
        }
    })
</script>