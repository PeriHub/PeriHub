<template>
    <v-container fluid style="height:100%;">
        <v-container fluid style="height:30%;">
            <v-row dense align="center" justify="center" style="height:30%;">
                <h1>Welcome to PeriHub!</h1>
            </v-row>
            <v-row dense align="center" justify="center" style="height:70%;">
                <p align="center" justify="center" style="max-width:870px;">
                Peridynamics is a non-local theory that overcomes discontinuity problems of the classical theory of continuum mechanics. It is an effective method to model fracture mechanics problems. PeriHub is a platform that provides a numerical implementation of the peridynamic theory. It is an extension of the open source Peridigm software.
                </p>
            </v-row>
        </v-container>
        <v-container fluid>
            <v-row justify="center">
                    <router-link class="card" to="perihub">
                        <v-card width="400px">
                        <v-img
                            src="../assets/dogbone.png"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>PeriHub</v-card-title>
                        </v-img>
                        </v-card>
                    </router-link>
                    <router-link class="card" to="guide">
                        <v-card width="400px">
                        <v-img
                            src="../assets/books.jpg"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>Guide</v-card-title>
                        </v-img>
                        </v-card>
                    </router-link>
                    <router-link class="card" to="publications">
                        <v-card width="400px">
                        <v-img
                            src="../assets/papers.jpg"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>Publications</v-card-title>
                        </v-img>
                        </v-card>
                    </router-link>
                    <div class="card">
                        <v-card width="400px" href="https://perihub-api.fa-services.intra.dlr.de/docs">
                        <v-img
                            src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>API</v-card-title>
                        </v-img>
                        </v-card>
                    </div>
                    <div class="card">
                        <v-card width="400px" href="https://gitlab.dlr.de/fa_sw/perihub">
                        <v-img
                            src="https://about.gitlab.com/images/press/logo/wm.svg"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>GitLab</v-card-title>
                        </v-img>
                        </v-card>
                    </div>
                    <div class="card">
                        <v-card width="400px" href="https://github.com/PeriDoX/PeriDoX">
                        <v-img
                            src="https://github.githubassets.com/images/modules/open_graph/github-mark.png"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>PeriDox</v-card-title>
                        </v-img>
                        </v-card>
                    </div>
            </v-row>
        </v-container>
    </v-container>
</template>

<script>

 import axios from 'axios'
//  import vueJsonEditor from 'vue-json-editor'
//  import VueJsonPretty from 'vue-json-pretty'
//  import 'vue-json-pretty/lib/styles.css'
import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere

// import highlighting library (you can use any library you want just return html string)
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles

import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
// import pdf from 'vue-pdf'
// import { colormap } from 'colormap';
// import RemoteComponent from "vue-remote-component";
import GIICmodelImage from '../assets/GIICmodel/GIICmodel.jpg'
import GIICmodelFile from '../assets/GIICmodel/GIICmodel.json'
import DCBmodelImage from '../assets/DCBmodel/DCBmodel.jpg'
import DCBmodelFile from '../assets/DCBmodel/DCBmodel.json'
import DogboneImage from '../assets/Dogbone/Dogbone.jpg'
import DogboneFile from '../assets/Dogbone/Dogbone.json'
import PeriHubImage from '../assets/PeriHub.png'
import { Plotly } from 'vue-plotly'
// import { faLessThanEqual } from '@fortawesome/free-solid-svg-icons';

  export default {
    name: 'PeriHub',
    components: {
      PrismEditor,
      Splitpanes,
      Pane,
      Plotly,
      // pdf
      // RemoteComponent
    },
    data () {
      return {
        }
    },
    methods: {
        viewInputFile(loadFile) {
            let headersList = {
            'Cache-Control': 'no-cache',
            'Authorization': this.authToken
            }
        },
    }
  }
</script>
<style>
  .card{
    text-decoration: none; 
    padding-right: 10px;
    padding-left: 10px;
    padding-top: 10px;
    padding-bottom: 10px;
  }
</style>