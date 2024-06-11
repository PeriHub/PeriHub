<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="justify-center">
    <div class="column full-width">
      <div class="row justify-center text-h3 q-pb-xl" style="padding: 20px; text-align:center">Welcome to PeriHub!</div>
      <div class="row text-subtitle2 justify-center" style="padding: 20px; text-align:center">
        PeriHub is a platform that provides a numerical implementation of
        the peridynamic theory. It is an extension of the open source
        PeriLab software. Peridynamics is a non-local theory that overcomes
        discontinuity problems of the classical theory of continuum
        mechanics. It is an effective method to model fracture mechanics
        problems.
      </div>
    </div>
    <div class="row justify-center full-width q-pa-md q-my-lg">
      <router-link class="card" to="perihub">
        <q-card class="my-card">
          <q-img src="~assets/dogbone.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              PeriHub
            </div>
          </q-img>
        </q-card>
      </router-link>
      <a class="card" href="https://perihub.github.io/PeriHub/">
        <q-card class="my-card">
          <q-img src="~assets/compass.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              Guide
            </div>
          </q-img>
        </q-card>
      </a>
      <router-link class="card" to="publications">
        <q-card class="my-card">
          <q-img src="~assets/books.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              Publications
            </div>
          </q-img>
        </q-card>
      </router-link>
      <router-link class="card" to="tools">
        <q-card class="my-card">
          <q-img src="~assets/tools.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              Tools
            </div>
          </q-img>
        </q-card>
      </router-link>
      <router-link class="card" to="api/docs">
        <q-card class="my-card">
          <q-img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              API
            </div>
          </q-img>
        </q-card>
      </router-link>
      <a class="card" href="https://github.com/PeriHub/PeriHub">
        <q-card class="my-card">
          <q-img src="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              GitHub
            </div>
          </q-img>
        </q-card>
      </a>
      <a class="card" href="https://perilab-results.nimbus-extern.dlr.de">
        <q-card class="my-card">
          <q-img src="~assets/perilab.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              PeriLab-Results
            </div>
          </q-img>
        </q-card>
      </a>
      <a class="card" href="https://www.youtube.com/@PeriHub">
        <q-card class="my-card">
          <q-img
            src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_(2017).svg/2560px-YouTube_full-color_icon_(2017).svg.png"
            height="200px">
            <div class="text-h5 absolute-bottom text-right">
              YouTube
            </div>
          </q-img>
        </q-card>
      </a>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'IndexPage'
})
</script>
<style>
.my-card {
  width: 400px;
}

.card {
  text-decoration: none;
  padding-right: 10px;
  padding-left: 10px;
  padding-top: 10px;
  padding-bottom: 10px;
}
</style>
