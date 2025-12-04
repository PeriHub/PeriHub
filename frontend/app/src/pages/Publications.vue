<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-page class="flex-center">
    <ul style="padding: 20px;">
      <q-list v-for="entry in bib_entries" :key="entry['entryTags']['URL']">
        <q-card flat bordered style="padding: 10px; margin: 10px;">
          <div v-if="entry['entryTags']['Title']">
            <div v-if="entry['entryTags']['URL']">
              <a :href="entry['entryTags']['URL']"><span class="title">{{ entry['entryTags']['Title'] }}</span></a>
            </div>
            <div v-if="entry['entryTags']['url']">
              <a :href="entry['entryTags']['url']"><span class="title">{{ entry['entryTags']['Title'] }}</span></a>
            </div>
            <div v-if="!entry['entryTags']['url'] && !entry['entryTags']['URL']">
              <span class="title">{{ entry['entryTags']['Title'] }}</span>
            </div>
          </div>
          <div v-if="entry['entryTags']['title']">
            <div v-if="entry['entryTags']['URL']">
              <a :href="entry['entryTags']['URL']"><span class="title">{{ entry['entryTags']['title'] }}</span></a>
            </div>
            <div v-if="entry['entryTags']['url']">
              <a :href="entry['entryTags']['url']"><span class="title">{{ entry['entryTags']['title'] }}</span></a>
            </div>
            <div v-if="!entry['entryTags']['url'] && !entry['entryTags']['URL']">
              <span class="title">{{ entry['entryTags']['title'] }}</span>
            </div>
          </div>
          <div v-if="entry['entryTags']['Author']">
            <span class="author">{{ entry['entryTags']['Author'] }}</span>
          </div>
          <div v-if="entry['entryTags']['author']">
            <span class="author">{{ entry['entryTags']['author'] }}</span>
          </div>
          <div>
            <span v-if="entry['entryTags']['Journal']"><em><span class="journal">{{
              entry['entryTags']['Journal']
                  }}</span></em>&nbsp;</span>
            <span v-if="entry['entryTags']['journal']"><em><span class="journal">{{
              entry['entryTags']['journal']
                  }}</span></em>&nbsp;</span>
            <span v-if="entry['entryTags']['Month']"><span class="month">{{ entry['entryTags']['Month']
                }}</span>,&nbsp;</span>
            <span v-if="entry['entryTags']['month']"><span class="month">{{ entry['entryTags']['month']
                }}</span>,&nbsp;</span>
            <span v-if="entry['entryTags']['Year']"><span class="year">{{ entry['entryTags']['Year'] }}</span></span>
            <span v-if="entry['entryTags']['year']"><span class="year">{{ entry['entryTags']['year'] }}</span></span>.
          </div>
        </q-card>
      </q-list>
    </ul>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
//@ts-expect-error Bla
import bibtexParse from "bibtex-parse-js";
import { getPublications } from 'src/client';

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
    _getPublications() {

      getPublications()
        .then((response: string) => {
          console.log(response)
          this.bib_data = this.latexToUtf(response)
          this.bib_entries = bibtexParse.toJSON(this.bib_data);
        })
        .catch((error: undefined) => {
          console.log(error)
          this.$q.notify({
            type: 'negative',
            message: error
          })
        })
    },
    latexToUtf(string: string) {
      return string.replace(/{\\"a}/gi, "ä");
    },
  },
  beforeMount() {
    this._getPublications();
  },
});
</script>

<style></style>
