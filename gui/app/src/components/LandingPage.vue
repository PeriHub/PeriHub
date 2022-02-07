<template>
    <v-container fluid class="pa-0" style="height:100%;">
        <div id="app" class="scroll">
            <v-container fluid style="height:30%; min-height:300px;">
                <v-row dense align="center" justify="center" style="height:30%; min-height:100px;">
                    <h1>Welcome to PeriHub!</h1>
                </v-row>
                <v-row dense align="center" justify="center" style="height:70%;">
                    <p align="center" justify="center" style="max-width:870px;">
                    Peridynamics is a non-local theory that overcomes discontinuity problems of the classical theory of continuum mechanics. It is an effective method to model fracture mechanics problems. PeriHub is a platform that provides a numerical implementation of the peridynamic theory. It is an extension of the open source Peridigm software.
                    </p>
                </v-row>
            </v-container>
            <v-container fluid  style="height:70%; min-height:450px;">
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
                                src="../assets/compass.jpg"
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
                                src="../assets/books.jpg"
                                class="white--text align-end"
                                gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                                height="200px">
                                <v-card-title>Publications</v-card-title>
                            </v-img>
                            </v-card>
                        </router-link>
                        <router-link class="card" to="conversion">
                            <v-card width="400px">
                            <v-img
                                src="../assets/math.jpg"
                                class="white--text align-end"
                                gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                                height="200px">
                                <v-card-title>Conversion</v-card-title>
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
        </div>
    </v-container>
</template>

<script>
  export default {
    name: 'PeriHub',
    components: {
    },
    data () {
      return {
        }
    },
    methods: {
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
  .scroll{
    height: 100%;
    overflow-y: scroll;
  }
</style>