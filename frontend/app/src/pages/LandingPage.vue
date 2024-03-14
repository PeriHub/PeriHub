<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="justify-center">
    <div class="column full-width">
      <div class="row justify-center text-h3 q-pb-xl" style="padding: 20px; text-align:center">Welcome to PeriHub!</div>
      <div class="row text-subtitle2 justify-center" style="padding: 20px; text-align:center">
        PeriHub is a platform that provides a numerical implementation of
        the peridynamic theory. It is an extension of the open source
        Peridigm software. Peridynamics is a non-local theory that overcomes
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
      <router-link class="card" to="guide">
        <q-card class="my-card">
          <q-img src="~assets/compass.jpg" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              Guide
            </div>
          </q-img>
        </q-card>
      </router-link>
      <router-link class="card" to="publications">
        <q-card class="my-card">
          <q-img src="~assets/books.jpg" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              Publications
            </div>
          </q-img>
        </q-card>
      </router-link>
      <router-link class="card" to="tools">
        <q-card class="my-card">
          <q-img src="~assets/math.jpg" height="200px">
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
      <a class="card" href="https://gitlab.com/dlr-perihub/PeriHub">
        <q-card class="my-card">
          <q-img src="https://about.gitlab.com/images/press/logo/wm.svg" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              GitLab
            </div>
          </q-img>
        </q-card>
      </a>
      <a class="card" href="https://github.com/PeriDoX/PeriDoX">
        <q-card class="my-card">
          <q-img src="https://github.githubassets.com/images/modules/open_graph/github-mark.png" height="200px">
            <div class="text-h5 absolute-bottom text-right">
              PeriDox
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
