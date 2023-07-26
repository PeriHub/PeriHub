<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-header elevated class="bg-primary text-white">
    <q-toolbar>
      <router-link style="text-decoration: none; color: inherit" to="/">
        <div class="row align-center">
          <img src="~assets/PeriHubLogo2b.png" style="height: 50px; margin: 5px; width: auto;">

          <!-- <q-toolbar-title>
              PeriHub
            </q-toolbar-title> -->
        </div>
      </router-link>
      <!-- <q-btn flat color="secondary" icon-right="mail" label="On Right"></q-btn>
          <q-btn flat round dense icon="gamepad"></q-btn> -->
      <!-- <router-link style="text-decoration: none; color: inherit" to="/">
            <div class="row">
              <q-img
                alt="DLR Logo"
                src="~assets/DLR_Signet_weiss.png"
                size="xs"
              />
              <h1>PeriHub</h1>
            </div>
          </router-link> -->

      <q-space></q-space>

      <q-tabs align="center">
        <q-route-tab to="/perihub" label="Perihub" />
        <q-route-tab to="/guide" label="Guide" />
        <q-route-tab to="/tools" label="Tools" />
        <q-route-tab to="/publications" label="Publications" />
      </q-tabs>

      <q-space></q-space>

      <q-toggle v-model="store.darkMode" @click="toggleDarkMode" checked-icon="dark_mode" color="red"
        unchecked-icon="light_mode"></q-toggle>

      <q-btn flat dense icon="fab fa-gitlab" href="https://gitlab.com/dlr-perihub/PeriHub">
        <q-tooltip>
          GitLab
        </q-tooltip>
      </q-btn>

      <q-btn flat dense icon="fas fa-bolt" href="https://perihub-api.fa-services.intra.dlr.de/docs">
        <q-tooltip>
          PeriHub-API
        </q-tooltip>
      </q-btn>

      <q-btn flat dense icon="fab fa-github" href="https://github.com/PeriDoX/PeriDoX">
        <q-tooltip>
          PeriDoX
        </q-tooltip>
      </q-btn>

    </q-toolbar>

  </q-header>
</template>

<script>
import { defineComponent } from 'vue'
import { useDefaultStore } from 'stores/default-store';
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
  methods: {
    toggleDarkMode() {
      localStorage.setItem("darkMode", this.store.darkMode);
      this.$q.dark.toggle();
    },
  }
})
</script>
<style></style>
