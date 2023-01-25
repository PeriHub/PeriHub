<template>
  <v-container fluid style="height: 100%">
    <v-row fluid style="height: 100%">
      <v-col cols="12" sm="2">
        <v-navigation-drawer padding-left="0">
          <v-list dense nav class="py-0">
            <v-list-item
              v-for="item in items"
              :key="item.title"
              link
              :to="item.route"
            >
              <v-list-item-icon>
                <i :class="item.icon"></i>
              </v-list-item-icon>

              <v-list-item-content>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
              </v-list-item-content>
            </v-list-item>

            <v-divider></v-divider>

            <v-list-group prepend-icon="fas fa-keyboard">
              <template v-slot:activator>
                <v-list-item-title>Input</v-list-item-title>
              </template>
              <v-list-item
                v-for="item in input"
                :key="item.title"
                link
                :to="item.route"
              >
                <v-list-item-title>{{ item.title }}</v-list-item-title>

                <v-list-item-icon>
                  <i :class="item.icon"></i>
                </v-list-item-icon>
              </v-list-item>
            </v-list-group>

            <v-list-group prepend-icon="fas fa-sign-out-alt">
              <template v-slot:activator>
                <v-list-item-title>Output</v-list-item-title>
              </template>
              <v-list-item
                v-for="item in output"
                :key="item.title"
                link
                :to="item.route"
              >
                <v-list-item-title>{{ item.title }}</v-list-item-title>

                <v-list-item-icon>
                  <i :class="item.icon"></i>
                </v-list-item-icon>
              </v-list-item>
            </v-list-group>

            <v-divider></v-divider>

            <v-list-group prepend-icon="fas fa-cubes">
              <template v-slot:activator>
                <v-list-item-title>Examples</v-list-item-title>
              </template>
              <v-list-item
                v-for="item in examples"
                :key="item.title"
                link
                :to="item.route"
              >
                <v-list-item-title>{{ item.title }}</v-list-item-title>

                <v-list-item-icon>
                  <i :class="item.icon"></i>
                </v-list-item-icon>
              </v-list-item>
            </v-list-group>
          </v-list>
        </v-navigation-drawer>
      </v-col>
      <v-col style="height: 100%; padding: 0px" cols="12" sm="10">
        <router-view class="view two" name="b"></router-view>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      items: [
        {
          title: "Introduction",
          icon: "fas fa-compass",
          route: "/guide/introduction",
        },
        {
          title: "Getting started",
          icon: "fas fa-tachometer-alt",
          route: "/guide/gettingStarted",
        },
        { title: "Buttons", icon: "fas fa-toggle-on", route: "/guide/buttons" },
        { title: "FAQ", icon: "fas fa-question", route: "/guide/faq" },
      ],
      input: [
        { title: "Model", icon: "fas fa-cube", route: "/guide/input/model" },
        {
          title: "Material",
          icon: "fas fa-toolbox",
          route: "/guide/input/material",
        },
        {
          title: "Damage Models",
          icon: "fas fa-cut",
          route: "/guide/input/damageModels",
        },
        { title: "Blocks", icon: "fas fa-th", route: "/guide/input/blocks" },
        {
          title: "Boundary Conditions",
          icon: "fas fa-project-diagram",
          route: "/guide/input/boundaryConditions",
        },
        {
          title: "Output",
          icon: "fas fa-sign-out-alt",
          route: "/guide/input/output",
        },
        {
          title: "Solver",
          icon: "fas fa-calculator",
          route: "/guide/input/solver",
        },
        { title: "Job", icon: "fas fa-flask", route: "/guide/input/job" },
      ],
      output: [
        {
          title: "Modelview",
          icon: "fas fa-eye",
          route: "/guide/output/modelview",
        },
        {
          title: "Textview",
          icon: "fas fa-edit",
          route: "/guide/output/textview",
        },
      ],
      examples: [
        {
          title: "Dogbone",
          icon: "fas fa-cube",
          route: "/guide/examples/dogbone",
        },
        {
          title: "GIICmodel",
          icon: "fas fa-cube",
          route: "/guide/examples/giicmodel",
        },
        {
          title: "DCBmodel",
          icon: "fas fa-cube",
          route: "/guide/examples/dcbmodel",
        },
        {
          title: "FE Files",
          icon: "fas fa-cube",
          route: "/guide/examples/fefiles",
        },
      ],
    };
  },
};
</script>
<style></style>
