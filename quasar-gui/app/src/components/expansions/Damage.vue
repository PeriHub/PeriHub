<template>
    <q-list bordered class="rounded-borders">
        <q-expansion-item
            expand-separator
            icon="fas fa-cut"
            label="Damage Models"
            caption="John Doe"
        >
            <q-list
                v-for="damage, index in damages"
                :key="damage.damagesId"
                style="padding: 0px"
            >
                <div v-bind:style="(damage.damagesId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                    <h4 class="my-title">Damage Model {{damage.damagesId}}</h4>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="damage.name"
                            :rules="[rules.required, rules.name]"
                            :label="damageKeys.name"
                            outlined
                            dense
                        ></q-input>
                        <q-btn flat icon="fas fa-trash-alt" @click="removeDamage(index)">
                            <q-tooltip>
                                Remove  Damage Model
                            </q-tooltip>
                        </q-btn>
                    </div>
                    <div class="row my-row">
                        <q-select 
                            class="my-input"
                            :options="damageModelName"
                            v-model="damage.damageModel"
                            :label="damageKeys.damageModel"
                            outlined
                            dense
                        ></q-select>
                    </div>
                    <div class="row my-row" v-if="damage.damageModel!='Von Mises Stress'">
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalStretch"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.criticalStretch"
                            clearable
                            outlined
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalEnergy"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.criticalEnergy"
                            clearable
                            outlined
                            dense
                            :readonly="damage.criticalEnergyCalc.calculateCriticalEnergy"
                        ></q-input>
                    </div>
                    <div class="row my-row" v-if="damage.damageModel=='Von Mises Stress'">
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalVonMisesStress"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.criticalVonMisesStress"
                            clearable
                            outlined
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalDamage"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.criticalDamage"
                            clearable
                            outlined
                            dense
                        ></q-input>
                    </div>
                    <div class="row my-row" v-if="damage.damageModel=='Von Mises Stress'">
                        <q-input 
                            class="my-input"
                            v-model="damage.thresholdDamage"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.thresholdDamage"
                            clearable
                            outlined
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalDamageToNeglect"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.criticalDamageToNeglect"
                            clearable
                            outlined
                            dense
                        ></q-input>
                    </div>
                    <q-toggle
                        class="my-toggle"
                        v-model="damage.criticalEnergyCalc.calculateCriticalEnergy"
                        label="Calculate Critical Energy"
                        dense
                    ></q-toggle>
                    <div class="row my-row" v-if="damage.criticalEnergyCalc.calculateCriticalEnergy">
                        <q-input 
                            class="my-input"
                            v-model="damage.criticalEnergyCalc.k1c"
                            :rules="[rules.required, rules.float]"
                            label="Fracture Toughness (K1C)"
                            clearable
                            outlined
                            dense
                        ></q-input>
                    </div>
                    <q-toggle
                        class="my-toggle"
                        v-model="damage.interBlockDamage"
                        label="Inter Block Damage"
                        dense
                    ></q-toggle>
                    <div v-if="damage.interBlockDamage">
                      <q-list
                        v-for="prop, subindex in damage.interBlocks"
                        :key="prop.damagesInterId"
                        style="padding: 0px"
                      >
                        <div class="row my-row">
                            <q-select 
                                class="my-input"
                                :options="blocks"
                                item-text="id"
                                v-model="prop.firstBlockId"
                                label="First Block Id"
                                outlined
                                dense
                            ></q-select>
                            <q-select 
                                class="my-input"
                                :options="blocks"
                                item-text="id"
                                v-model="prop.secondBlockId"
                                label="Second Block Id"
                                outlined
                                dense
                            ></q-select>
                            <q-input 
                                class="my-input"
                                v-model="prop.value"
                                :rules="[rules.required, rules.float]"
                                label="Critical Energ"
                                outlined
                                dense
                            ></q-input>
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
                    <q-toggle
                        class="my-toggle"
                        v-model="damage.onlyTension"
                        :label="damageKeys.onlyTension"
                        dense
                    ></q-toggle>
                    <div class="row my-row">
                        <q-select 
                            class="my-input"
                            :options="stabilizatonType"
                            v-model="damage.stabilizatonType"
                            :label="damageKeys.stabilizatonType"
                            outlined
                            dense
                        ></q-select>
                    </div>
                    <q-toggle
                        class="my-toggle"
                        v-model="damage.detachedNodesCheck"
                        :label="damageKeys.detachedNodesCheck"
                        dense
                    ></q-toggle>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="damage.thickness"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.thickness"
                            outlined
                            dense
                        ></q-input>
                    </div>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="damage.hourglassCoefficient"
                            :rules="[rules.required, rules.float]"
                            :label="damageKeys.hourglassCoefficient"
                            outlined
                            dense
                        ></q-input>
                    </div>
                </div>
                <q-separator></q-separator>
            </q-list>
            <q-btn flat icon="fas fa-plus" @click="addDamage">
                <q-tooltip>
                    Add Damage Model
                </q-tooltip>
            </q-btn>
        </q-expansion-item>
    </q-list>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
    import { deepCopy } from '../../utils/functions.js'
  
    export default defineComponent({
        name: 'DamageSettings',
        setup() {
            const store = useModelStore();
            const damages = computed(() => store.modelData.damages)
            const blocks = computed(() => store.modelData.blocks)
            const bus = inject('bus')
            return {
                store,
                damages,
                blocks,
                rules,
                bus
            }
        },
        created() {
        },
        data() {
            return {
                damageModelName: [
                    "Critical Stretch",
                    "Von Mises Stress",
                    "Interface Aware",
                    "Time Dependent Critical Stretch",
                    "Critical Energy",
                    "Initial Damage",
                    "Time Dependent Critical Stretch",
                    "Critical Energy Correspondence",
                ],
                damageKeys: {
                    name: "name",
                    damageModel: "Damage Model",
                    criticalStretch: "Critical Stretch",
                    criticalEnergy: "Critical Energy",
                    interBlockDamage: "Interblock Damage",
                    numberOfBlocks: "Number of Blocks",
                    interBlockCriticalEnergy: "Interblock Critical Energy",
                    planeStress: "Plane Stress",
                    onlyTension: "Only Tension",
                    detachedNodesCheck: "Detached Nodes Check",
                    thickness: "Thickness",
                    hourglassCoefficient: "Hourglass Coefficient",
                    stabilizatonType: "Stabilizaton Type",
                },
                stabilizatonType: [
                    "Bond Based",
                    "State Based",
                    "Sub Horizon",
                    "Global Stiffness",
                ],
            };
        },
        methods: {
            addDamage() {
                const len = this.damages.length;
                let newItem = deepCopy(this.damages[len - 1])
                newItem.damagesId = len + 1
                newItem.name = "Damage" + (len + 1)
                this.damages.push(newItem);
            },
            removeDamage(index) {
                this.damages.splice(index, 1);
                if (this.damages.length == 0) {
                    for (var i = 0; i < this.blocks.length; i++) {
                    this.blocks[i].damageModel = "";
                    }
                }
            },
            addInterBlock(index) {
                const len = this.damages[index].interBlocks.length;
                let newItem = deepCopy(this.damages[index].interBlocks[len - 1])
                newItem.damagesInterId = len + 1
                newItem.firtsId = 1
                newItem.secondId = len + 1
                this.damages[index].interBlocks.push(newItem);
            },
            removeInterBlock(index, subindex) {
                this.damages[index].interBlocks.splice(subindex, 1);
            },
        }
    })
</script>
<style>
.my-title {
    margin-top: 10px;
    margin-bottom: 0px;
    margin-left: 10px;
}
.my-row {
    min-height: 50px;
}
.my-input {
    margin-left: 10px;
}
.my-toggle {
    height: 40px;
    margin: 10px;
}
</style>