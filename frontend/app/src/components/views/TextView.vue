<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
    <q-scroll-area style="height:calc(100% - 15px);">
        <prism-editor v-model="viewStore.textOutput" :highlight="highlighter" line-numbers></prism-editor>
    </q-scroll-area>
</template>

<script>
    import { defineComponent } from 'vue'
    import { useViewStore } from 'stores/view-store';
    
    import { PrismEditor }    rom "vue-prism-edito    ;
    import        e-prism-editor/d            ismeditor                "; // import the styles somewhere
    import { hi            t,         ua    s }    rom "prism        omponents/prism-core";
    import        ismjs/com            s/prism        ke    
      import "p        js/compon        /pr    m-javascript";
    import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles
    export default defineComponent({
        name: 'TextView',
        components:{
            PrismEditor
        },
        setup() {
            const viewStore = useViewStore();

            return {
                viewStore,
            }
        },
        data() {
            return {
                textHeight: "400px",
            };
        },
        methods: {
            highlighter(code) {
                return highlight(code, languages.js); // languages.<insert language> to return html with markup
            },
        },
    })
</script>

<style></style>
