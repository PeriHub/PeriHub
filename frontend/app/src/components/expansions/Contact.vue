<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="contact.enabled" label="Enabled" standout dense></q-toggle>
    <div v-if="contact.enabled">
      <div class="row my-row">
        <q-input class="my-input" v-model="contact.searchRadius" :rules="[rules.required, rules.float]"
          label="Search Radius" standout dense></q-input>
        <q-input class="my-input" v-model="contact.searchFrequency" :rules="[rules.required, rules.int]"
          label="Search Frequency" standout dense></q-input>
      </div>
      <q-separator></q-separator>
      <q-list v-for="contactModel, index in contact.contactModels" :key="contactModel.contactModelId"
        style="padding: 0px">
        <div class="row my-row">
          <q-input class="my-input" v-model="contactModel.name" :rules="[rules.required, rules.name]" label="Name"
            standout dense></q-input>
          <q-select class="my-input" :options="contactType" v-model="contactModel.contactType" label="Type" standout
            dense></q-select>
          <q-input class="my-input" v-model="contactModel.contactRadius" :rules="[rules.required, rules.float]"
            label="Contact Radius" standout dense></q-input>
          <q-input class="my-input" v-model="contactModel.springConstant" :rules="[rules.required, rules.float]"
            label="Spring Constant" standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeContactModel(index)">
            <q-tooltip>
              Remove Contact Model
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addContactModel">
        <q-tooltip>
          Add Contact Model
        </q-tooltip>
      </q-btn>
      <q-separator></q-separator>
      <q-list v-for="interaction, index in contact.interactions" :key="interaction.contactInteractionsId"
        style="padding: 0px">
        <div class="row my-row">
          <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
            v-model="interaction.firstBlockId" label="First Block Id" standout dense></q-select>
          <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
            v-model="interaction.secondBlockId" label="Second Block Id" standout dense></q-select>
          <q-select class="my-input" :options="contact.contactModels" option-label="contactModelsId"
            option-value="contactModelsId" emit-value v-model="interaction.contactModelId" label="Contact Model Id"
            standout dense></q-select>
          <q-btn flat icon="fas fa-trash-alt" @click="removeInteraction(index)">
            <q-tooltip>
              Remove Interaction
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addInteraction">
        <q-tooltip>
          Add Interaction
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { inject } from 'vue'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'ContactSettings',
  setup() {
    const store = useModelStore();
    const blocks = computed(() => store.modelData.blocks)
    const contact = computed(() => store.modelData.contact)
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
      contactType: ['Short Range Force'],
      // contactKeys: {
      //     name: 'Block Names',
      //     material: 'Material',
      //     damageModel: 'Damage Model',
      //     horizon: 'Horizon',
      // },
    };
  },
  methods: {
    addContactModel() {
      const len = this.contact.contactModels.length;
      let newItem = structuredClone(this.contact.contactModels[len - 1])
      newItem.contactModelsId = len + 1
      newItem.name = 'Contact Model ' + (len + 1)
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
