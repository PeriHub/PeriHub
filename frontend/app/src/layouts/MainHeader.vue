<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-header elevated class="bg-primary text-white">
    <q-toolbar>
      <router-link style="text-decoration: none; color: inherit" to="/">
        <q-img src="~assets/PeriHubLogo2b.png" style="height: 50px; margin: 5px; width: 50px;"></q-img>
      </router-link>
      <!-- <q-toolbar-title>PeriHub</q-toolbar-title> -->
      <q-space></q-space>

      <q-tabs align="center">
        <q-route-tab to="/perihub" label="Perihub" />
        <q-route-tab to="/models" label="Models" />
        <q-route-tab to="/tools" label="Tools" />
        <q-route-tab to="/publications" label="Publications" />
      </q-tabs>

      <q-space></q-space>

      <q-toggle v-model="store.saveEnergy" checked-icon="eco" color="green" unchecked-icon="bolt"></q-toggle>

      <q-toggle v-model="store.darkMode" @click="toggleDarkMode" checked-icon="dark_mode" color="red"
        unchecked-icon="light_mode"></q-toggle>

      <q-btn flat dense icon="fas fa-compass" href="https://perihub.github.io/PeriHub/">
        <q-tooltip>
          Documentations
        </q-tooltip>
      </q-btn>

      <q-btn flat dense icon="fab fa-github" href="https://github.com/PeriHub/PeriHub">
        <q-tooltip>
          GitHub
        </q-tooltip>
      </q-btn>

      <q-btn flat dense icon="fas fa-bolt" to="/api/docs">
        <q-tooltip>
          PeriHub-API
        </q-tooltip>
      </q-btn>

      <q-btn flat dense icon="fab fa-youtube" href="https://www.youtube.com/@PeriHub">
        <q-tooltip>
          YouTube
        </q-tooltip>
      </q-btn>

    </q-toolbar>

  </q-header>
</template>

<script>
import { defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
export default defineComponent({
  name: "MainHeader",
  setup() {
    const store = useDefaultStore();
    return {
      store,
    }
  },
  data() {
    return {
    };
  },
  mounted() {
    if (localStorage.getItem("saveEnergy")) {
      this.store.saveEnergy = localStorage.getItem("saveEnergy") == "true";
    }
  },
  methods: {
    toggleDarkMode() {
      localStorage.setItem("darkMode", this.store.darkMode);
      this.$q.dark.toggle();
    },
  },
  watch: {
    'store.saveEnergy': {
      handler() {
        console.log("saveEnergy changed!");
        localStorage.setItem("saveEnergy", JSON.stringify(this.store.saveEnergy));
      },
      deep: true,
    },
  }
})
</script>
<style></style>
