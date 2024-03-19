<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <div>
        <q-toggle class="my-toggle" v-model="contact.enabled" label="Enabled" standout dense></q-toggle>
        <div v-if="contact.enabled">
            <div class="row my-row">
                <q-input class="my-input" v-model="co        ntact.searchRadius" :rules="[rules.required, rules.float]"
                    label="Search Radius" standout dense></q-input>
                <q-input class="my-input" v-model="contact.searchFrequency" :rules="[rules.required, rules.int]"
                    label="Search Frequency" standout dense></q-input>
            </div>
            <q-separator></q-separator>
            <q-list v-for="contactMo        del, index in contact.contactModels" :key="contactModel.        contactModelId"
                style="padding: 0px">
                <div class="row my-row">
                    <q-input class="my-input" v-model="contactModel.name" :rules="[rules.req        uired, rules.name]"
                        label="Name" standout dense></q-input>
                    <q-select class="my-input" :options="contactType" v-model="contactMod        el.contactType" label="Type"
                        standout dense></q-select>
                    <q-input class="my-input" v-model="co        ntactModel.contactRa        dius"
                        :rules="[rules.required,         rules.float]" label="Contact Radius" standout dense></q-input>
                    <q-input class="my-input" v-model="contactModel.springConstant"
                        :rules="[        rules.required, rules        .float]" label="Spring Constant" standout dense></q-input>
                    <q-btn flat icon="fas fa-trash-alt" @click="removeCont        actModel(index)">
                        <q-tooltip>
                            Remove Contact Model
                        </q-tooltip>
                    </q-btn>
                </div>
                <q-separator></q-separator>
            </q-list>

            <q-btn flat icon="fas fa-plus" @click="addCo        ntactModel">
                <q-tooltip>
                    Add Contact Model
                </q-tooltip>
            </q-btn>
            <q-separator></q-separator>
            <q-list v-for="interaction, index in contact.interactions" :key="interacti        on.contactInteractionsId"
                style="padding: 0px">
                <div class="row my-row">
                    <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId"
                        emit-value v-model="inte        raction.firstBlockId" label="First Block Id" standout dense></q-select>
                    <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId"
                        emit-value v-model="i        nteraction.secondBlockId" label="Second Block Id" standout
                        dense></q-select>
                    <q-select class="my-input" :options="contact.contactModels" option-label="contactModelsId"
                        option-value="contactModelsId" emit-value v-model="int        eraction.contactModelId"
                        label="Contact Model Id" standout dense></q-select>
                    <q-btn flat icon="fas fa-trash-alt" @click="removeInteraction(index)">
                        <q-tooltip>
                            Remove Interaction
                        </q-tooltip>
                    </q-btn>
                </div>
                <q-separator></q-separator>
            </q-list>

            <q-btn flat icon="fas fa-plus" @click="addInt        eraction">
                <q-tooltip>
                    Add Interaction
                </q-tooltip>
            </q-btn>
        </div>
    </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'stores/model-store';
import { inject } from 'vue    import rules from "a    ets/rules.js        export default d            omponent(                me: 'ContactSettings',
    setup() {
        cons            e =        Mo    lSt    e();
             onst blocks = computed(() => stor        delData.b            
              ns    con    ct = comp        (() => st        mod    Data.contact)
        const bus = inject('bus')
        return {
            store,
            blocks,
            contact,
            rules,
            bus
        }
    },
    created() {
    },
    data() {
        return {
            contactType: ["Short Range Force"],
            // contactKeys: {
            //     name: "Block Names",
            //     material: "Material",
            //     damageModel: "Damage Model",
            //     horizon: "Horizon",
            // },
        };
    },
    methods: {
        addContactModel() {
            const len = this.contact.contactModels.length;
            let newItem = structuredClone(this.contact.contactModels[len - 1])
            newItem.contactModelsId = len + 1
            newItem.name = "Contact Model " + (len + 1)
            this.contact.contactModels.push(newItem);
        },
        removeContactModel(index) {
            this.contact.contactModels.splice(index, 1);
        },
        addInteraction() {
            const len = this.contact.interactions.length;
            let newItem = structuredClone(this.contact.interactions[len - 1])
            newItem.contactInteractionsId = len + 1
            this.contact.interactions.push(newItem);
        },
        removeInteraction(index) {
            this.contact.interactions.splice(index, 1);
        },
    }
})
</script>