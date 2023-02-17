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
      <q-expansion-item
        expand-separator
        icon="fas fa-keyboard"
        label="Input"
        caption="John Doe"
      >
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
      <q-expansion-item
        expand-separator
        icon="fas fa-sign-out-alt"
        label="Output"
        caption="John Doe"
      >
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
      <q-expansion-item
        expand-separator
        icon="fas fa-cubes"
        label="Examples"
        caption="John Doe"
      >
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
        ],
        input: [
          { label: "Model", icon: "fas fa-cube", route: "/guide/input/model" },
          {
            label: "Material",
            icon: "fas fa-toolbox",
            route: "/guide/input/material",
          },
          {
            label: "Damage Models",
            icon: "fas fa-cut",
            route: "/guide/input/damageModels",
          },
          { label: "Blocks", icon: "fas fa-th", route: "/guide/input/blocks" },
          {
            label: "Boundary Conditions",
            icon: "fas fa-project-diagram",
            route: "/guide/input/boundaryConditions",
          },
          {
            label: "Output",
            icon: "fas fa-sign-out-alt",
            route: "/guide/input/output",
          },
          {
            label: "Solver",
            icon: "fas fa-calculator",
            route: "/guide/input/solver",
          },
          { label: "Job", icon: "fas fa-flask", route: "/guide/input/job" },
        ],
        output: [
          {
            label: "Modelview",
            icon: "fas fa-eye",
            route: "/guide/output/modelview",
          },
          {
            label: "Textview",
            icon: "fas fa-edit",
            route: "/guide/output/textview",
          },
        ],
        examples: [
          {
            label: "Dogbone",
            icon: "fas fa-cube",
            route: "/guide/examples/dogbone",
          },
          {
            label: "GIICmodel",
            icon: "fas fa-cube",
            route: "/guide/examples/giicmodel",
          },
          {
            label: "DCBmodel",
            icon: "fas fa-cube",
            route: "/guide/examples/dcbmodel",
          },
          {
            label: "FE Files",
            icon: "fas fa-cube",
            route: "/guide/examples/fefiles",
          },
        ],
      };
    },
  })
  </script>
  <style></style>
  