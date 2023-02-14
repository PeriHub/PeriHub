<template>
    <VuePlotly 
        v-if="store.viewId==2"
        :data="plotData"
        :layout="plotLayout"
        :options="plotOptions"
        :display-mode-bar="true"
    >
    </VuePlotly >
</template>

<script>
    import { defineComponent } from 'vue'
    import { VuePlotly  } from 'vue3-plotly'
    import { useViewStore } from 'stores/view-store';
    export default defineComponent({
        name: 'PlotlyView',
        components:{
            VuePlotly 
        },
        setup() {
            const store = useViewStore();
            return {
                store,
            }
        },
        data() {
            return {
                plotRawData: "",
                plotData: [
                    {
                    name: "Displacement",
                    x: [1, 2, 3, 4],
                    y: [10, 15, 20, 17],
                    type: "scatter",
                    },
                ],
                plotLayout: {
                    // title: 'this.model.modelNameSelected',
                    showlegend: true,
                    // margin: { t: 50 },
                    hovermode: "compare",
                    bargap: 0,
                    xaxis: {
                    showgrid: true,
                    zeroline: true,
                    color: "white",
                    },
                    yaxis: {
                    showgrid: true,
                    zeroline: true,
                    color: "white",
                    },
                    xaxis2: {
                    showgrid: false,
                    zeroline: false,
                    },
                    yaxis2: {
                    showgrid: true,
                    zeroline: false,
                    },
                    plot_bgcolor: "#2D2D2D",
                    paper_bgcolor: "#2D2D2D",
                    font: {
                    color: "white",
                    },
                    modebar: {
                    color: "white",
                    // color: "#6E6E6E"
                    },
                },
                plotOptions: {
                    scrollZoom: true,
                    setBackground: "black",
                },
            };
        },
        methods: {},
    })
</script>

<style>
</style>
