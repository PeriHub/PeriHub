<template>
   <prism-editor
        class="my-editor"
        v-model="viewStore.textOutput"
        :highlight="highlighter"
        line-numbers
    ></prism-editor>
</template>

<script>
    import { defineComponent } from 'vue'
    import { useViewStore } from 'stores/view-store';
    
    import { PrismEditor } from "vue-prism-editor";
    import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere
    import { highlight, languages } from "prismjs/components/prism-core";
    import "prismjs/components/prism-clike";
    import "prismjs/components/prism-javascript";
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
            };
        },
        methods: {
            highlighter(code) {
                return highlight(code, languages.js); // languages.<insert language> to return html with markup
            },
        },
    })
</script>

<style>
</style>
