<template>
    <v-container fluid style="height:100%;">
        <v-row dense align="center" justify="center" style="height:20%;">
            <h1>Welcome to PeriHub!</h1>
        </v-row>
        <v-container fluid>
            <v-row justify="center">
                    <router-link class="card" to="home">
                        <v-card width="400px">
                        <v-img
                            src="../assets/PeriHub.png"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>PeriHub</v-card-title>
                        </v-img>
                        </v-card>
                    </router-link>
                    <div class="card" to="home">
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
                    <router-link class="card" to="guide">
                        <v-card width="400px">
                        <v-img
                            src="https://static.vecteezy.com/system/resources/previews/000/263/066/original/book-icon-vector.jpg"
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
                            src="http://www.umsl.edu/psychology/thrive/photos/stock/publications.jpg"
                            class="white--text align-end"
                            gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                            height="200px">
                            <v-card-title>Publications</v-card-title>
                        </v-img>
                        </v-card>
                    </router-link>
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
        cards: [
            { title: 'PeriHub', src: '../assets/PeriHub.png', flex: 4, routes: "home" },
            { title: 'API', src: 'https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png', flex: 4, routes: "home" },
            { title: 'Documentation', src: 'https://cdn.vuetifyjs.com/images/cards/plane.jpg', flex: 4, routes: "home" },
            { title: 'Documentation', src: 'https://cdn.vuetifyjs.com/images/cards/plane.jpg', flex: 4, routes: "home" },
            ],
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