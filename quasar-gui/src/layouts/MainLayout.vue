<template>
  <q-layout view="hHh lpR fFf">

    <q-header elevated class="bg-primary text-white" style="height: 60px;">
      <q-toolbar>
        <router-link style="text-decoration: none; color: inherit" to="/">
          <div class="row align-center">
            <img src="~assets/DLR_Signet_weiss.png" style="height: 50px;">

            <q-toolbar-title>
              PeriHub
            </q-toolbar-title>
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

        <q-toggle
          v-model="store.darkMode"
          @click="toggleDarkMode"
          checked-icon="dark_mode"
          color="red"
          unchecked-icon="light_mode"
        ></q-toggle>

        <q-btn flat dense icon="fab fa-gitlab" href="https://gitlab.dlr.de/fa_sw/peridynamik/perihub">
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

      <!-- <q-tabs align="left">
        <q-route-tab to="/page1" label="Page One" />
        <q-route-tab to="/page2" label="Page Two" />
        <q-route-tab to="/page3" label="Page Three" />
      </q-tabs> -->
    </q-header>

    <q-drawer v-model="drawerActive" side="left" bordered>
      <GuideDrawer></GuideDrawer>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>

    <q-footer elevated class="bg-grey-8 text-white">
      <q-toolbar>
        <div class="row" justify="center" no-gutters>
          <q-btn
            href="https://www.dlr.de/fa"
            color="white"
            text
            rounded
            class="my-0"
          >
            ABOUT US
          </q-btn>
          <q-btn
            href="https://leichtbau.dlr.de/"
            color="white"
            text
            rounded
            class="my-0"
          >
            BLOG
          </q-btn>
          <q-btn
            href="mailto:Jan-Timo.Hesse@dlr.de"
            color="white"
            text
            rounded
            class="my-0"
          >
            CONTACT US
          </q-btn>
          <div
            class="col lighten-2 py-0 text-center white--text"
            color="#464646"
            cols="12"
          >
            {{ new Date().getFullYear() }} — <strong>PeriHub</strong> | Jan-Timo
            Hesse | Christian Willberg | Falk Heinecke
          </div>
        </div>
      </q-toolbar>
    </q-footer>

  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue';
import { useDefaultStore } from 'stores/default-store';
import GuideDrawer from 'components/GuideDrawer.vue'

export default defineComponent({
  name: 'MainLayout',
  data() {
    return {
      drawerActive: false
    }
  },
  components: {
    GuideDrawer
  },
  setup() {
    const store = useDefaultStore();
    return {
      store,
    }
  },
  methods: {
    toggleDarkMode() {
      // this.store.toggleDarkMode();
      this.$q.dark.toggle();
    },
    initializeDarkMode() {
      this.$q.dark.set(localStorage.getItem("darkMode") == "true");
    },
  },
  async beforeMount() {
    await this.store.initialiseStore();
    this.initializeDarkMode();
    this.drawerActive = this.$router.currentRoute.value.path === '/guide'
  },
  watch: {
    $route() {
      this.drawerActive = this.$router.currentRoute.value.path === '/guide'
    }
  },

})
</script>
