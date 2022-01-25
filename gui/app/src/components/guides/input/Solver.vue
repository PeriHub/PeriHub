<template>
    <v-container fluid class="pa-0" style="height:100%">
        <div id="app" class="scroll">
          <v-container fluid class="pa-0" style="height:100%">
            <vue-markdown :source="markdown"></vue-markdown>
          </v-container>
        </div>
    </v-container>
</template>

<script>
  import axios from 'axios'
  import VueMarkdown from 'vue-markdown'

  export default {
    name: 'PeriHub',
    components: {  
      VueMarkdown
    },
    data () {
      return {
        markdown:  "",
        url: 'https://perihub-api.fa-services.intra.dlr.de/'
      }
    },
    methods: {
      async getDocs(){

        let reqOptions = {
            url: this.url + "getDocs",
            params: {Name: "input/Solver",
                     model: false},
            method: "GET"
        }

        await axios.request(reqOptions).then(response => (
        this.markdown = response.data))
      },
    },
    beforeMount() {
      if(process.env.VUE_APP_ROOT_API!=undefined)
      {
          this.url = process.env.VUE_APP_ROOT_API
        //   console.log("changed URL: " + process.env.VUE_APP_ROOT_API)
      }
      this.getDocs();
    }
  }
</script>
<style>
  .scroll{
    height: 100%;
    overflow-y: scroll;
  }
  img[alt=drawing] { width: 1000px; }
</style>