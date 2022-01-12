<template>
  <v-app class="main">
    <div class="header"> 
      <v-app-bar 
        app
        color="#464646"
        dark
      >
        <router-link style="text-decoration: none; color: inherit;" to="/">
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
        </router-link>

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
              href="https://gitlab.dlr.de/fa_sw/perihub"
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
              href="https://perihub-api.fa-services.intra.dlr.de/docs"
              target="_blank"
              color="primary"
              v-on="on"
            >
              <i
                class="fas fa-bolt"
                size="2x"
              />
            </v-btn>
          </template>
          <span>PeriHub-API</span>
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
    </div>

    <div class="body"> 
      <router-view class="view one" name="a"></router-view>
    </div>

    <div class="footer">
    
      <v-footer
        color="#464646"
        padless
      >
        <v-row
          justify="center"
          no-gutters
        >
          <v-btn
            href="https://www.dlr.de/fa"
            color="white"
            text
            rounded
            class="my-2"
          >
            ABOUT US 
          </v-btn>
          <v-btn
            href="https://leichtbau.dlr.de/"
            color="white"
            text
            rounded
            class="my-2"
          >
            BLOG
          </v-btn>
          <v-btn
            href="mailto:Jan-Timo.Hesse@dlr.de"
            color="white"
            text
            rounded
            class="my-2"
          >
            CONTACT US
          </v-btn>
          <v-col
            class="lighten-2 py-2 text-center white--text"
            color="#464646"
            cols="12"
          >
            {{ new Date().getFullYear() }} — <strong>PeriHub</strong> | Jan-Timo Hesse | Christian Willberg | Falk Heinecke 
          </v-col>
        </v-row>
      </v-footer>
    </div>
  </v-app>
</template>

<script>
import Home from './components/Home';

export default {
  name: 'App',
  metaInfo: {
    title: 'PeriHub',
    // titleTemplate: '%s | vue-meta Example App',
    htmlAttrs: {
      lang: 'en-US'
    },
    meta: [
      { charset: 'utf-8' },
      // { name: 'description', content: 'An example Vue application with vue-meta.' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' }
    ]
  },
  components: {
    Home,
  },

  data: () => ({
    //
  }),
  methods: {
    saveDarkMode() {
      this.$cookie.set('darkMode', this.$vuetify.theme.dark, Infinity, '/app');
    },
    getDarkMode() {
      var dark = this.$cookie.get('darkMode')
      if(dark=='true'){
        this.$vuetify.theme.dark = true;
      }
    }
  },
  mounted(){
    this.getDarkMode()
  },
};
</script>

<style>
.my-btn {
  margin-right: 5px;
}
.v-app {
  height: 100%;
  width: 100%;
}
.v-footer {
  padding-top: 0px;
  padding-bottom: 0px;
}
::-webkit-scrollbar {
  display: none;
}
.main {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.body {
  height: 88vh;
  flex: auto;
}
.header {
  flex: none;
  height: 64px;
}
.footer {
  flex: none;
  height: 92px;
}
</style>
