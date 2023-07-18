<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

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
            markdown: "",
        };
    },
    computed: {
        output() {
            return marked(this.markdown)
        }
    },
    methods: {
        async getDocs(route) {

            let params = {
                name: route
            }
            this.$api.get('/docs/getDocs', { params })
                .then((response) => {
                    this.markdown = response.data
                })
                .catch((error) => {
                    this.$q.notify({
                        type: 'negative',
                        message: error.response.data.detail
                    })
                })
        }

    },
    beforeMount() {
        this.getDocs(this.$route.params.id);
    },
    beforeRouteUpdate(to, from, next) {
        this.getDocs(to.params.id);
        next();
    },
};
</script>

<style>
.output {
    overflow: auto;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    padding: 0 20px;
}

img {
    width: 100%;
}
</style>