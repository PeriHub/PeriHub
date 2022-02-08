<template>
    <v-container fluid class="pa-0" style="height:100%">
        <div id="app" class="scroll">
          <v-container fluid class="pa-0" style="height:100%">
            <markdown-it-vue class="md-body" :content="markdown"/>
          </v-container>
        </div>
    </v-container>
</template>

<script>
  import axios from 'axios'
  // import VueMarkdown from 'vue-markdown'
  import MarkdownItVue from 'markdown-it-vue'

  export default {
    name: 'PeriHub',
    components: {  
      // VueMarkdown
      MarkdownItVue
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
            params: {Name: "input/Material",
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