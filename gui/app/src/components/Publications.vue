<template>
    <v-container fluid class="pa-0" style="height:100%">
        <div id="app" class="scroll">
            <v-container>
                <h1>Publications</h1>
                <ul>
                    <li v-for="entry in bib_entries">
                        <div v-if="entry.entryTags.Title">
                            <div v-if="entry.entryTags.URL">
                                <a :href="entry.entryTags.URL"><span class="title">{{ entry.entryTags.Title }}</span></a>
                            </div>
                            <div v-if="entry.entryTags.url">
                                <a :href="entry.entryTags.url"><span class="title">{{ entry.entryTags.Title }}</span></a>
                            </div>
                            <div v-if="!entry.entryTags.url & !entry.entryTags.URL">
                                <span class="title">{{ entry.entryTags.Title }}</span>
                            </div>
                        </div>
                        <div v-if="entry.entryTags.title">
                            <div v-if="entry.entryTags.URL">
                                <a :href="entry.entryTags.URL"><span class="title">{{ entry.entryTags.title }}</span></a>
                            </div>
                            <div v-if="entry.entryTags.url">
                                <a :href="entry.entryTags.url"><span class="title">{{ entry.entryTags.title }}</span></a>
                            </div>
                            <div v-if="!entry.entryTags.url & !entry.entryTags.URL">
                                <span class="title">{{ entry.entryTags.title }}</span>
                            </div>
                        </div>
                        <div v-if="entry.entryTags.Author">
                            <span class="author">{{ entry.entryTags.Author }}</span>
                        </div>
                        <div v-if="entry.entryTags.author">
                            <span class="author">{{ entry.entryTags.author }}</span>
                        </div>
                        <div>
                            <span v-if="entry.entryTags.Journal"><em><span class="journal">{{ entry.entryTags.Journal }}</span></em>&nbsp;</span>
                            <span v-if="entry.entryTags.journal"><em><span class="journal">{{ entry.entryTags.journal }}</span></em>&nbsp;</span>
                            <span v-if="entry.entryTags.Month"><span class="month">{{ entry.entryTags.Month }}</span>,&nbsp;</span>
                            <span v-if="entry.entryTags.month"><span class="month">{{ entry.entryTags.month }}</span>,&nbsp;</span>
                            <span v-if="entry.entryTags.Year"><span class="year">{{ entry.entryTags.Year }}</span></span>
                            <span v-if="entry.entryTags.year"><span class="year">{{ entry.entryTags.year }}</span></span>.
                        </div>
                    </li>
                </ul>
            </v-container>
        </div>
    </v-container>
</template>

<script>
    import axios from 'axios'
    import bibtexParse from "bibtex-parse-js";
    // import bibFile from '../static/test.bib'

    export default {
        components: {
            bibtexParse
        },
        data () {
            return {
                url: 'https://perihub-api.fa-services.intra.dlr.de/',
                bib_data: '',
                bib_entries: []
            }
        },
        methods: {
            async getPublications(){

                let reqOptions = {
                    url: this.url + "getPublications",
                    method: "GET"
                }

                await axios.request(reqOptions).then(response => (
                this.bib_data = this.latexToUtf(response.data)))
                this.bib_entries =  bibtexParse.toJSON(this.bib_data)
                // console.log(this.bib_data);
                // console.log(this.bib_entries);
            },
            latexToUtf(string){

                return string.replace(/{\\\"a}/gi,"ä")
            }
        },
        created: function() {
        },
        beforeMount() {
        // console.log("beforeMount")
            if(process.env.VUE_APP_ROOT_API!=undefined)
            {
                this.url = process.env.VUE_APP_ROOT_API
                // console.log("changed URL: " + process.env.VUE_APP_ROOT_API)
            }
            this.getPublications();
        }
    }
</script>
<style>
  .scroll{
    height: 100%;
    overflow-y: scroll;
  }
</style>