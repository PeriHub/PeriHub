<template>
    <div class="output" v-html="output"></div>
</template>

<script>
import { api } from 'boot/axios'
import { marked } from 'marked'

export default {
    name: "GuidePage",
    data() {
        return {
            markdown: "# hellodrtghr",
            url: "https://perihub-api.fa-services.intra.dlr.de/",
        };
    },
    computed: {
        output() {
        return marked(this.markdown)
        }
    },
    methods: {
        async getDocs() {

            api.get('/getDocs', {name: "Buttons", model: false})
            .then((response) => {
                this.markdown = response.data
            })
            .catch(() => {
                this.$q.notify({
                    color: 'negative',
                    position: 'top',
                    message: 'Loading failed',
                    icon: 'report_problem'
                })
            })
        }

    },
    beforeMount() {
        // if (process.env.VUE_APP_DEV != undefined) {
        // this.url = "http://localhost:6020/";
        // // console.log("changed URL: " + process.env.VUE_APP_DEV)
        // }
        this.getDocs();
    },
};
</script>

<style>
.output {
    overflow: auto;
    width: 50%;
    height: 100%;
    box-sizing: border-box;
    padding: 0 20px;
  }
</style>