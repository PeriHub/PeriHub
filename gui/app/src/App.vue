<template>
  <v-app class="overflow-hidden">
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
          src="./assets/DLR_Signet_weiss.png"
          transition="scale-transition"
          width="40"
        />
        <h1> PeriHub </h1>
      </div>

      <v-spacer />
      <v-switch
        v-model="$vuetify.theme.dark"
        @change="saveDarkMode"
        hide-details
      />
      <v-tooltip bottom>
        <template #activator="{ on, attrs }">
          <v-btn
            class="my-btn"
            v-bind="attrs"
            href="https://gitlab.dlr.de/AG-SATT/modelgenerator"
            target="_blank"
            color="primary"
            v-on="on"
          >
            <i
              class="fab fa-gitlab"
              size="2x"
            />
          </v-btn>
        </template>
        <span>GitLab</span>
      </v-tooltip>
      <v-tooltip bottom>
        <template #activator="{ on, attrs }">
          <v-btn
            class="my-btn"
            v-bind="attrs"
            href="https://github.com/PeriDoX/PeriDoX"
            target="_blank"
            color="primary"
            v-on="on"
          >
            <i
              class="fab fa-github"
              size="2x"
            />
          </v-btn>
        </template>
        <span>PeriDoX</span>
      </v-tooltip>
    </v-app-bar>

    <v-main>
      <Generator />
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
  methods: {
    saveDarkMode() {
      this.$cookie.set('darkMode', this.$vuetify.theme.dark, Infinity, '/app');
    },
    getDarkMode() {
      this.$vuetify.theme.dark = this.$cookie.get('darkMode');
    }
  },
  beforeMount(){
    this.getDarkMode()
  },
};
</script>

<style>
.my-btn {
  margin-right: 5px;
}
.v-app {
  height: 600px;
  width: 100%;
}
</style>
