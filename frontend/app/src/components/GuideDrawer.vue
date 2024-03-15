<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-scroll-area class="fit">
    <q-list>
      <template v-for="(menuItem, index) in items" :key="index">
        <q-item clickable :active="menuItem.label === 'Outbox'" v-ripple link :to="menuItem.route">
          <q-item-section avatar>
            <q-icon :name="menuItem.icon"></q-icon>
          </q-item-section>
          <q-item-section>
            {{ menuItem.label }}
          </q-item-section>
        </q-item>
      </template>
      <q-separator></q-separator>
      <q-expansion-item expand-separator icon="fas fa-cubes" label="Examples">
        <template v-for="(menuItem, index) in examples" :key="index">
          <q-item clickable :active="menuItem.label === 'Outbox'" v-ripple link :to="menuItem.route">
            <q-item-section avatar>
              <q-icon :name="menuItem.icon"></q-icon>
            </q-item-section>
            <q-item-section>
              {{ menuItem.label }}
            </q-item-section>
          </q-item>
        </template>
      </q-expansion-item>
      <q-separator></q-separator>

    </q-list>
  </q-scroll-area>
</template>
  
<script>
  import { defineComponent } from 'vue'
  export default defineComponent({
    name: "GuideDrawer",
    data() {
      return {
        items: [
          {
            label: "Introduction",
            icon: "fas fa-compass",
            route: "/guide/introduction",
          },
          {
            label: "Getting started",
            icon: "fas fa-tachometer-alt",
            route: "/guide/gettingStarted",
          },
          { label: "Buttons", icon: "fas fa-toggle-on", route: "/guide/buttons" },
          { label: "FAQ", icon: "fas fa-question", route: "/guide/faq" },
          { label: "Output", icon: "fas fa-eye", route: "/guide/output" },
        ],
        examples: [
          {
            label: "Dogbone",
            icon: "fas fa-cube",
            route: "/guide/examples_Dogbone",
          },
          {
            label: "GIICmodel",
            icon: "fas fa-cube",
            route: "/guide/examples_Giicmodel",
          },
          {
            label: "DCBmodel",
            icon: "fas fa-cube",
            route: "/guide/examples_Dcbmodel",
          },
          {
            label: "FE Files",
            icon: "fas fa-cube",
            route: "/guide/examples_Fefiles",
          },
        ],
      };
    },
  })
  </script>
<style></style>
  