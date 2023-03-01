<template>
    <q-page class="flex-center">
        <h1>Publications</h1>
        <ul>
          <q-list v-for="entry in bib_entries" :key="entry.entryTags.URL">
            <div v-if="entry.entryTags.Title">
              <div v-if="entry.entryTags.URL">
                <a :href="entry.entryTags.URL"
                  ><span class="title">{{ entry.entryTags.Title }}</span></a
                >
              </div>
              <div v-if="entry.entryTags.url">
                <a :href="entry.entryTags.url"
                  ><span class="title">{{ entry.entryTags.Title }}</span></a
                >
              </div>
              <div v-if="!entry.entryTags.url & !entry.entryTags.URL">
                <span class="title">{{ entry.entryTags.Title }}</span>
              </div>
            </div>
            <div v-if="entry.entryTags.title">
              <div v-if="entry.entryTags.URL">
                <a :href="entry.entryTags.URL"
                  ><span class="title">{{ entry.entryTags.title }}</span></a
                >
              </div>
              <div v-if="entry.entryTags.url">
                <a :href="entry.entryTags.url"
                  ><span class="title">{{ entry.entryTags.title }}</span></a
                >
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
              <span v-if="entry.entryTags.Journal"
                ><em
                  ><span class="journal">{{
                    entry.entryTags.Journal
                  }}</span></em
                >&nbsp;</span
              >
              <span v-if="entry.entryTags.journal"
                ><em
                  ><span class="journal">{{
                    entry.entryTags.journal
                  }}</span></em
                >&nbsp;</span
              >
              <span v-if="entry.entryTags.Month"
                ><span class="month">{{ entry.entryTags.Month }}</span
                >,&nbsp;</span
              >
              <span v-if="entry.entryTags.month"
                ><span class="month">{{ entry.entryTags.month }}</span
                >,&nbsp;</span
              >
              <span v-if="entry.entryTags.Year"
                ><span class="year">{{ entry.entryTags.Year }}</span></span
              >
              <span v-if="entry.entryTags.year"
                ><span class="year">{{ entry.entryTags.year }}</span></span
              >.
            </div>
          </q-list>
        </ul>
    </q-page>
</template>

<script>
import { api } from 'boot/axios'
import { defineComponent } from 'vue'
import bibtexParse from "bibtex-parse-js";


export default defineComponent({
    name: "PublicationPage",
    components: {
        // bibtexParse,
    },
    data() {
        return {
        bib_data: "",
        bib_entries: [],
        };
    },
    methods: {
        async getPublications() {

            api.get('/getPublications')
            .then((response) => {
                this.bib_data = this.latexToUtf(response.data)
                this.bib_entries = bibtexParse.toJSON(this.bib_data);
            })
            .catch((error) => {
                this.$q.notify({
                    type: 'negative',
                    message: error.response.data.detail
                })
            })
        },
        latexToUtf(string) {
            return string.replace(/{\\\"a}/gi, "ä");
        },
    },
    beforeMount() {
        this.getPublications();
    },
});
</script>

<style>
</style>