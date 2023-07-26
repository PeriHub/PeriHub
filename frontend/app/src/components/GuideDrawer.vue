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
      <q-expansion-item expand-separator icon="fas fa-keyboard" label="Input">
        <template v-for="(menuItem, index) in input" :key="index">
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
      <q-expansion-item expand-separator icon="fas fa-sign-out-alt" label="Output">
        <template v-for="(menuItem, index) in output" :key="index">
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
            route: "/guide/Introduction",
          },
          {
            label: "Getting started",
            icon: "fas fa-tachometer-alt",
            route: "/guide/GettingStarted",
          },
          { label: "Buttons", icon: "fas fa-toggle-on", route: "/guide/Buttons" },
          { label: "FAQ", icon: "fas fa-question", route: "/guide/FAQ" },
        ],
        input: [
          { label: "Model", icon: "fas fa-cube", route: "/guide/input_Model" },
          {
            label: "Material",
            icon: "fas fa-toolbox",
            route: "/guide/input_Material",
          },
          {
            label: "Damage Models",
            icon: "fas fa-cut",
            route: "/guide/input_DamageModels",
          },
          { label: "Blocks", icon: "fas fa-th", route: "/guide/input_Blocks" },
          {
            label: "Boundary Conditions",
            icon: "fas fa-project-diagram",
            route: "/guide/input_BoundaryConditions",
          },
          {
            label: "Output",
            icon: "fas fa-sign-out-alt",
            route: "/guide/input_Output",
          },
          {
            label: "Solver",
            icon: "fas fa-calculator",
            route: "/guide/input_Solver",
          },
          { label: "Job", icon: "fas fa-flask", route: "/guide/input_Job" },
        ],
        output: [
          {
            label: "Modelview",
            icon: "fas fa-eye",
            route: "/guide/output_Modelview",
          },
          {
            label: "Textview",
            icon: "fas fa-edit",
            route: "/guide/output_Textview",
          },
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
  