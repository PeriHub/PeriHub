<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="contact.enabled" label="Enabled" standout dense></q-toggle>
    <div v-if="contact.enabled">
      <div class="row my-row">
        <q-input class="my-input" v-model="contact.searchFrequency" :rules="[rules.required, rules.int]"
          label="Search Frequency" standout dense></q-input>
        <q-toggle class="my-toggle" v-model="contact.onlySurfaceContactNodes" label="Only Surface Contact Nodes"
          standout dense></q-toggle>
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
          <q-input class="my-input" v-model="contactModel.contactStiffness" :rules="[rules.required, rules.float]"
            label="Contact Stiffness" standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeContactModel(index)">
            <q-tooltip>
              Remove Contact Model
            </q-tooltip>
          </q-btn>
        </div>

        <q-separator></q-separator>

        <q-list v-for="contactGroup, subindex in contactModel.contactGroups" :key="contactGroup.contactGroupId"
          style="padding: 0px">
          <div class="row my-row">
            <q-input class="my-input" v-model="contactGroup.name" :rules="[rules.required, rules.name]" label="Name"
              standout dense></q-input>
            <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
              v-model="contactGroup.masterBlockId" label="Master Block Id" standout dense></q-select>
            <q-select class="my-input" :options="blocks" option-label="blocksId" option-value="blocksId" emit-value
              v-model="contactGroup.slaveBlockId" label="Slave Block Id" standout dense></q-select>
            <q-input class="my-input" v-model="contactGroup.searchRadius" :rules="[rules.required, rules.float]"
              label="Search Radius" standout dense></q-input>
            <q-btn flat icon="fas fa-trash-alt" @click="removeContactGroup(index, subindex)">
              <q-tooltip>
                Remove Contact Group
              </q-tooltip>
            </q-btn>
          </div>
          <q-separator></q-separator>
        </q-list>

        <q-btn flat icon="fas fa-plus" @click="addContactGroup(index)">
          <q-tooltip>
            Add Contact Group
          </q-tooltip>
        </q-btn>

        <q-separator></q-separator>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addContactModel">
        <q-tooltip>
          Add Contact Model
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { Contact, ContactGroup, ContactModel } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'ContactSettings',
  setup() {
    const store = useModelStore();
    const blocks = computed(() => store.modelData.blocks)
    const contact = computed(() => store.modelData.contact) as unknown as Contact
    return {
      store,
      blocks,
      contact,
      rules
    }
  },
  data() {
    return {
      contactType: ['Penalty Contact'],
      // contactKeys: {
      //     name: 'Block Names',
      //     material: 'Material',
      //     damageModel: 'Damage Model',
      //     horizon: 'Horizon',
      // },
    };
  },
  methods: {
    addContactGroup(index) {
      if (!this.contact.contactModels[index]!.contactGroups) {
        this.contact.contactModels[index]!.contactGroups = []
      }
      const len = this.contact.contactModels[index]!.contactGroups.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.contact.contactModels[index]!.contactGroups[len - 1])) : {} as ContactGroup;
      newItem.contactGroupId = len + 1
      newItem.name = 'Contact Group ' + (len + 1)
      this.contact.contactModels[index]!.contactGroups.push(newItem);
    },
    removeContactGroup(index, subindex) {
      this.contact.contactModels[index]!.contactGroups.splice(subindex, 1);
    },
    addContactModel() {
      if (!this.contact.contactModels) {
        this.contact.contactModels = []
      }
      const len = this.contact.contactModels.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.contact.contactModels[len - 1])) : {} as ContactModel;
      newItem.contactGroupId = len + 1
      newItem.name = 'Contact Model ' + (len + 1)
      this.contact.contactModels.push(newItem);
    },
    removeContactModel(index) {
      this.contact.contactModels.splice(index, 1);
      this.contact.contactModels.forEach((model, i) => {
        model.contactGroupId = i + 1
      })
    },
  }
})
</script>
