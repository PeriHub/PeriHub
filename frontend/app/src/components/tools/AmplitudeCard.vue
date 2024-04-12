<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <q-card bordered>
    <q-card-section>
      <div class="text-h6">Amplitude Generator</div>
      <!-- <div class="text-subtitle2">Enter two constants to run the calculations</div> -->
    </q-card-section>

    <q-separator inset></q-separator>

    <q-card-section>
      <q-splitter v-model="verticalSplitterModel" class="body" :limits="[30, 60]">
        <template v-slot:before>
          <div class="col">
            <q-input class="my-input" v-model="amplitude.max" label="Max" standout dense></q-input>
            <q-input class="my-input" v-show="amplitude.type != 'Type 2'" v-model="amplitude.min" label="Min" standout
              dense></q-input>
            <q-input class="my-input" v-model="amplitude.frequency" label="Frequency" standout dense></q-input>
            <q-input class="my-input" v-model="amplitude.end" label="Time" standout dense></q-input>
            <!-- <q-input class="my-input" v-show="amplitude.type == 'Sinus'" v-model="amplitude.t_max" label="t Max"
              standout dense></q-input> -->
            <q-select class="my-select" :options="amplitudeTypes" v-model="amplitude.type" label="Type of Amplitude"
              standout dense></q-select>
          </div>
        </template>

        <template v-slot:after>
          <q-tabs v-model="tab_id" dense class="text-grey" active-color="primary" indicator-color="primary"
            align="justify" color="deep-purple accent-4" left max-width="1100">
            <q-tab name="plotly" label="Plotly"></q-tab>
            <q-tab name="output" label="Output"></q-tab>
          </q-tabs>

          <q-tab-panels v-model="tab_id" animated style="height:100%">
            <q-tab-panel name="plotly">
              <q-card>
                <VuePlotly :data="plotData" :layout="plotLayout" :options="plotOptions" :display-mode-bar="true"
                  :autoResize="true" :scrollZoom="true">
                </VuePlotly>
              </q-card>
            </q-tab-panel>
            <q-tab-panel name="output">
              <q-card>
                <prism-editor class="my-editor" v-model="valueOutput" :highlight="highlighter"
                  line-numbers></prism-editor>
              </q-card>
            </q-tab-panel>
          </q-tab-panels>
        </template>
      </q-splitter>
    </q-card-section>
  </q-card>
</template>

<script>
import { defineComponent } from 'vue'
import { VuePlotly } from 'vue3-plotly'
import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles
export default defineComponent({
  name: 'AmplitudeCard',
  components: {
    PrismEditor,
    VuePlotly,
  },
  data() {
    return {
      verticalSplitterModel: 50,
      tab_id: "plotly",
      amplitudeTypes: ["Type 1", "Type 2", "Sinus"],
      amplitude: {
        max: 10,
        min: 2,
        frequency: 5,
        end: 5,
        type: "Type 1",
        t_max: 1,
      },
      valueOutput: "A*sin(B*(t-C))+D",
      plotData: [
        {
          name: "Load",
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
    }
  },
  methods: {
    highlighter(code) {
      return highlight(code, languages.js); // languages.<insert language> to return html with markup
    },
    plot() {
      let tempData = structuredClone(this.plotData);
      tempData[0].x = [];
      tempData[0].y = [];
      var n = 10 * this.amplitude.frequency;
      var max = parseFloat(this.amplitude.max);
      var min = parseFloat(this.amplitude.min);
      var frequency = parseFloat(this.amplitude.frequency);
      var end = parseFloat(this.amplitude.end);
      for (var i = 0; i < n; i++) {
        var t = (i / (n - 1)) * end;
        tempData[0].x[i] = t;
        for (var j = 0; j < frequency; j++) {
          if (j == 0) {
            if (t <= (1 / frequency) * end) {
              tempData[0].y[i] = (t / ((1 / frequency) * end)) * max;
              break;
            }
          } else if (j % 2 != 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              tempData[0].y[i] =
                max -
                ((t - (j / frequency) * end) / ((1 / frequency) * end)) *
                (max - min);
              break;
            }
          } else if (j % 2 == 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              tempData[0].y[i] =
                min +
                ((t - (j / frequency) * end) / ((1 / frequency) * end)) *
                (max - min);
              break;
            }
          }
        }
      }
      this.plotData = structuredClone(tempData);
      this.valueOutput =
        "double max = " +
        this.amplitude.max.toString() +
        ";\n" +
        "double min = " +
        this.amplitude.min.toString() +
        ";\n" +
        "double frequency = " +
        this.amplitude.frequency.toString() +
        ";\n" +
        "double end = " +
        this.amplitude.end.toString() +
        ";\n" +
        "int idx = 0;\n" +
        "while (idx < frequency) \\{\n" +
        " if (idx == 0) \\{\n" +
        "   if (t <= 1 / frequency *end) \\{\n" +
        "     value = (t / ((1 / frequency) * end)) * max;\n" +
        "   \\}\n" +
        " \\}\n" +
        " else if (idx % 2 != 0) \\{\n" +
        "   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) \\{\n" +
        "     value = max - ((t - (idx / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n" +
        "   \\}\n" +
        " \\}\n" +
        " else if (idx % 2 == 0) \\{\n" +
        "   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) \\{\n" +
        "     value = min + ((t - (idx / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n" +
        "   \\}\n" +
        " \\}\n" +
        " idx = idx + 1;\n" +
        "\\}\n";
    },
    plot2() {
      let tempData = structuredClone(this.plotData);
      tempData[0].x = [];
      tempData[0].y = [];
      var n = 1000;
      var max = parseFloat(this.amplitude.max);
      var frequency = parseFloat(this.amplitude.frequency);
      var end = parseFloat(this.amplitude.end);
      for (var i = 0; i < n; i++) {
        var t = (i / (n - 1)) * end;
        tempData[0].x[i] = t;
        for (var j = 0; j < frequency; j++) {
          if (j == 0) {
            if (t <= (1 / frequency) * end) {
              tempData[0].y[i] = (t / end) * max * 2;
              break;
            }
          } else if (j % 2 != 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              tempData[0].y[i] =
                (j / frequency) * max * 2 - ((j - 1) / frequency) * max;
              break;
            }
          } else if (j % 2 == 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              tempData[0].y[i] =
                ((t - ((j / 2) * end) / frequency) / end) * max * 2;
              break;
            }
          }
        }
      }
      this.plotData = structuredClone(tempData);
      // this.plotData[0].x = time.split(",");
      this.valueOutput =
        "double max = " +
        this.amplitude.max.toString() +
        ";\n" +
        "double frequency = " +
        this.amplitude.frequency.toString() +
        ";\n" +
        "double end = " +
        this.amplitude.end.toString() +
        ";\n" +
        "int idx = 0;\n" +
        "while (idx < frequency) \\{\n" +
        " if (idx == 0) \\{\n" +
        "   if (t <= 1 / frequency *end) \\{\n" +
        "     value = (t / end) * max * 2;\n" +
        "   \\}\n" +
        " \\}\n" +
        " else if (idx % 2 != 0) \\{\n" +
        "   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) \\{\n" +
        "     value = (idx / frequency) * max * 2 - ((idx - 1) / frequency) * max;\n" +
        "   \\}\n" +
        " \\}\n" +
        " else if (idx % 2 == 0) \\{\n" +
        "   if ((idx / frequency *end < t) && (t <= (idx + 1) / frequency *end)) \\{\n" +
        "     value = ((t - ((idx / 2) * end) / frequency) / end) * max * 2;\n" +
        "   \\}\n" +
        " \\}\n" +
        " idx = idx + 1;\n" +
        "\\}\n";
    },
    sin() {
      let tempData = structuredClone(this.plotData);
      tempData[0].x = [];
      tempData[0].y = [];
      var n = 100 * this.amplitude.frequency;
      var max = parseFloat(this.amplitude.max);
      var min = parseFloat(this.amplitude.min);
      // var t_max = parseFloat(this.amplitude.t_max);
      var offset = (max + min) / 2;
      var frequency = parseFloat(this.amplitude.frequency);
      var end = parseFloat(this.amplitude.end);
      var R = (max - min) / 2; // Konstante Amplitude
      for (var i = 0; i < n; i++) {
        var t = (i / (n - 1)) * end;
        tempData[0].x[i] = t;
        tempData[0].y[i] = R * Math.sin(2 * Math.PI * frequency * t - Math.PI / 2) + offset; // Sinuskurve mit konstanter Amplitude
      }
      this.plotData = structuredClone(tempData);
      this.valueOutput = R.toString() + " * sin(2 * pi * " + this.amplitude.frequency.toString() + " * t - pi / 2) + " + offset.toString();
    },

  },
  mounted() {
    if (localStorage.getItem("amplitude")) {
      this.amplitude = JSON.parse(localStorage.getItem("amplitude"));
    }
    if (this.amplitude.type == "Type 1") {
      this.plot();
    } else if (this.amplitude.type == "Type 2") {
      this.plot2();
    } else if (this.amplitude.type == "Sinus") {
      this.sin();
    }
  },
  watch: {
    amplitude: {
      handler() {
        console.log("amplitude changed!");
        if (this.amplitude.type == "Type 1") {
          this.plot();
        } else if (this.amplitude.type == "Type 2") {
          this.plot2();
        } else if (this.amplitude.type == "Sinus") {
          this.sin();
        }
        localStorage.setItem("amplitude", JSON.stringify(this.amplitude));
      },
      deep: true,
    },
  }
})
</script>
<style scoped>
.my-input {
  margin-left: 10px;
}
</style>
