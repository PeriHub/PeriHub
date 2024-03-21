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

<script>
import { defineComponent } from 'vue';
import { useDefaultStore } from 'stores/default-store';
import { useModelStore } from 'stores/model-store';
import MainHeader from 'layouts/MainHeader.vue'
import MainFooter from 'layouts/MainFooter.vue'

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
  methods: {
    initializeDarkMode() {
      this.$q.dark.set(localStorage.getItem("darkMode") == "true");
    },
  },
  async beforeMount() {
    await this.modelStore.initialiseStore();
    if (localStorage.getItem("darkMode") == "true") {
      this.store.darkMode = true;
      this.$q.dark.toggle();
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
