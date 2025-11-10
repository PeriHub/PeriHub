<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-layout view="hHh lpR fFf">

    <MainHeader />

    <q-page-container>
      <router-view />
    </q-page-container>

    <MainFooter />

  </q-layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import MainHeader from 'layouts/MainHeader.vue'
import MainFooter from 'layouts/MainFooter.vue'
import { getValves, getConfig } from 'src/client'

export default defineComponent({
  name: 'MainLayout',
  data() {
    return {
    }
  },
  components: {
    MainHeader,
    MainFooter,
  },
  setup() {
    const store = useDefaultStore();
    const modelStore = useModelStore();
    return {
      store,
      modelStore
    }
  },
  created() {
    this.$bus.on('resetData', () => {
      this.resetData()
    })
  },
  methods: {
    initializeDarkMode() {
      this.$q.dark.set(localStorage.getItem("darkMode") == "true");
    },
    resetData() {
      getConfig({ configFile: this.modelStore.selectedModel.file }).then((response) => {
        this.modelStore.modelData = structuredClone(response)
      })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.body.detail
          })
        })
      getValves({ modelName: this.modelStore.selectedModel.file }).then((response) => {
        this.modelStore.modelParams = structuredClone(response)
      }).catch((error) => {
        this.$q.notify({
          type: 'negative',
          message: error.body.detail
        })
      })
    },
  },
  beforeMount() {
    this.store.initialiseStore();
    this.modelStore.initialiseStore();
    if (localStorage.getItem("darkMode") == "true") {
      this.store.darkMode = true;
      this.$q.dark.toggle();
    }
    if (!localStorage.getItem('modelData')) {
      console.log('beforeMount');
      this.resetData()
    }
  },
  watch: {
    modelStore: {
      handler() {
        console.log("model changed!");
        localStorage.setItem("modelData", JSON.stringify(this.modelStore.modelData));
      },
      deep: true,
    },
  }
})
</script>
