<template>
  <v-app>
    <v-app-bar 
      app
      color="#464646"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="DLR Logo"
          class="shrink mr-2"
          contain
          src="./assets/DLR_Signet_schwarz.png"
          transition="scale-transition"
          width="40"
        />
        <h1> Peridynamic Model Generator </h1>
      </div>

      <v-spacer></v-spacer>
      <v-switch hide-details v-model="$vuetify.theme.dark" />
      <v-btn icon @click="$refs.view.resetCamera()">
        <v-icon>mdi-crop-free</v-icon>
      </v-btn>
      <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
        <v-btn v-bind="attrs" v-on="on" href="https://gitlab.dlr.de/AG-SATT/modelgeneratorgui" target="_blank" color="primary">
            <i class="fab fa-gitlab" size="2x"></i>
        </v-btn>
      </template>
        <span>GitLab</span>
      </v-tooltip>
    </v-app-bar>

    <v-main>
      <Generator/>
    </v-main>
  </v-app>
</template>

<script>
import Generator from './components/Generator';

export default {
  name: 'App',

  components: {
    Generator,
  },

  data: () => ({
    //
  }),
};
</script>
