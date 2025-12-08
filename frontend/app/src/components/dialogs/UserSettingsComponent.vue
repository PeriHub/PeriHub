<template>
  <q-card style="width: 550px" class="q-px-sm q-pb-md">
    <q-card-section class="row items-center q-pb-none">
      <div class="text-h6">Settings</div>
      <q-space />
      <q-btn icon="close" flat round dense v-close-popup />
    </q-card-section>

    <!-- API Key Input -->


    <q-item-label header>Logged in as: {{ store.username }}</q-item-label>
    <q-item-label header v-if="store.TRIAL">Trial mode enabled, different features are disabled! </q-item-label>
    <q-item-label header v-if="store.cluster != ''">Configured Cluster: {{ store.cluster }}</q-item-label>
    <q-item-label header> PeriHub Version: {{ version.current }} / {{ version.latest }}</q-item-label>
    <q-item-label header> Perilab Version: {{ version.perilab_current }} / {{ version.perilab_latest }}</q-item-label>
    <!-- <q-item dense>
      <q-item-section avatar>
        <q-icon name="link" />
      </q-item-section>
      <q-item-section>
        <q-input class="my-input" v-model="store.shepardUrl" :rules="[rules.required, rules.name]"
          label="Shepard API URL" standout dense clearable @update:model-value="updateShepardEndpoint"></q-input>
      </q-item-section>
    </q-item>
    <q-item dense>
      <q-item-section avatar>
        <q-icon name="key" />
      </q-item-section>
      <q-item-section>
        <q-input class="my-input" v-model="store.apiKey" :rules="[rules.required, rules.name]" label="API Key" standout
          dense type="password" clearable @update:model-value="updateApiKey"></q-input>
      </q-item-section>
    </q-item> -->
  </q-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import rules from 'assets/rules.js';
import { useDefaultStore } from 'stores/default-store';
import { getVersion } from 'src/client';
import type { VersionData } from 'src/client';
// import { client } from '../../client/client.gen';

export default defineComponent({
  name: 'UserSettingsComponent',
  setup() {
    const store = useDefaultStore();

    return {
      rules,
      store,
    }
  },
  data() {
    return {
      version: {} as VersionData,
      bib_entries: [],
    };
  },
  methods: {
  },
  async beforeMount() {

    await getVersion().then((response) => this.version = response)
  }
});
</script>
