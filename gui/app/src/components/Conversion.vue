<template>
  <v-container fluid class="pa-0" style="height: 100%">
    <div id="app" class="scroll">
      <v-container>
        <h1>Conversion of elastic isotrpoic constants</h1>
        <p>Enter two constants to run the calculations</p>
        <v-row>
          <v-card width="400px">
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.bulkModulus"
                :label="materialKeys.bulkModulus"
                clearable
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.shearModulus"
                :label="materialKeys.shearModulus"
                clearable
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.youngsModulus"
                :label="materialKeys.youngsModulus"
                clearable
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.poissonsRatio"
                :label="materialKeys.poissonsRatio"
                clearable
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.pWaveModulus"
                :label="materialKeys.pWaveModulus"
                clearable
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="constants.lameFirst"
                :label="materialKeys.lameFirst"
                clearable
                outlined
              ></v-text-field>
            </v-col>
          </v-card>
          <v-card width="400px">
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.bulkModulus"
                :label="materialKeys.bulkModulus"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('bulkModulus')"
                id="bulkModulus"
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.shearModulus"
                :label="materialKeys.shearModulus"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('shearModulus')"
                id="shearModulus"
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.youngsModulus"
                :label="materialKeys.youngsModulus"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('youngsModulus')"
                id="youngsModulus"
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.poissonsRatio"
                :label="materialKeys.poissonsRatio"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('poissonsRatio')"
                id="poissonsRatio"
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.pWaveModulus"
                :label="materialKeys.pWaveModulus"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('pWaveModulus')"
                id="pWaveModulus"
                outlined
              ></v-text-field>
            </v-col>
            <v-col class="textfield-col">
              <v-text-field
                v-model="calculated.lameFirst"
                :label="materialKeys.lameFirst"
                :append-icon="'mdi-content-copy'"
                @click:append="copyText('lameFirst')"
                id="lameFirst"
                outlined
              ></v-text-field>
            </v-col>
          </v-card>
        </v-row>
      </v-container>
      <v-container max-width="1100">
        <h1>Amplitude Generator</h1>
        <splitpanes style="height: 100%">
          <pane min-size="10" size="30" style="height: 100%">
            <v-card width="400px">
              <v-col class="textfield-col">
                <v-text-field
                  v-model="amplitude.max"
                  label="Max"
                  outlined
                  type="number"
                ></v-text-field>
              </v-col>
              <v-col class="textfield-col" v-show="amplitude.type == 'Type 1'">
                <v-text-field
                  v-model="amplitude.min"
                  label="Min"
                  outlined
                  type="number"
                ></v-text-field>
              </v-col>
              <v-col class="textfield-col">
                <v-text-field
                  v-model="amplitude.frequency"
                  label="Frequency"
                  outlined
                  type="number"
                ></v-text-field>
              </v-col>
              <v-col class="textfield-col">
                <v-text-field
                  v-model="amplitude.end"
                  label="Time"
                  outlined
                  type="number"
                ></v-text-field>
              </v-col>
              <v-col class="textfield-col">
                <v-select
                  :items="amplitudeTypes"
                  v-model="amplitude.type"
                  label="Type of Amplitude"
                  outlined
                ></v-select>
              </v-col>
            </v-card>
          </pane>

          <pane min-size="30" size="70" style="height: 100%">
            <v-tabs color="deep-purple accent-4" left max-width="1100">
              <v-tab>Plotly</v-tab>
              <v-tab>Output</v-tab>
              <v-tab-item>
                <v-card>
                  <plotly
                    :data="plotData"
                    :layout="plotLayout"
                    :options="plotOptions"
                    :display-mode-bar="true"
                    :autoResize="true"
                    :scrollZoom="true"
                  >
                  </plotly>
                </v-card>
              </v-tab-item>
              <v-tab-item>
                <v-card>
                  <prism-editor
                    class="my-editor"
                    v-model="valueOutput"
                    :highlight="highlighter"
                    line-numbers
                  ></prism-editor>
                </v-card>
              </v-tab-item>
            </v-tabs>
          </pane>
        </splitpanes>
      </v-container>
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import bibtexParse from "bibtex-parse-js";
import { Plotly } from "vue-plotly";
// import bibFile from '../static/test.bib'
import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere

// import highlighting library (you can use any library you want just return html string)
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles

import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";

export default {
  components: {
    PrismEditor,
    Splitpanes,
    Pane,
    bibtexParse,
    Plotly,
  },
  data() {
    return {
      constants: {
        bulkModulus: null,
        shearModulus: null,
        youngsModulus: null,
        poissonsRatio: null,
        pWaveModulus: null,
        lameFirst: null,
      },
      calculated: {
        bulkModulus: null,
        shearModulus: null,
        youngsModulus: null,
        poissonsRatio: null,
        pWaveModulus: null,
        lameFirst: null,
      },
      materialKeys: {
        bulkModulus: "Bulk Modulus (K)",
        shearModulus: "Shear Modulus (G)",
        youngsModulus: "Young's Modulus (E)",
        poissonsRatio: "Poisson's Ratio (v)",
        pWaveModulus: "P-wave modulus (M)",
        lameFirst: "Lamé's first parameter (m)",
      },
      amplitudeTypes: ["Type 1", "Type 2"],
      amplitude: {
        max: 10,
        min: 2,
        frequency: 5,
        end: 5,
        type: "Type 1",
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
    };
  },
  props: ["plotid"],
  methods: {
    highlighter(code) {
      return highlight(code, languages.js); // languages.<insert language> to return html with markup
    },
    convert() {
      const K = this.constants.bulkModulus;
      const E = this.constants.youngsModulus;
      const L = this.constants.lameFirst;
      const G = this.constants.shearModulus;
      const v = this.constants.poissonsRatio;
      const M = this.constants.pWaveModulus;
      if (K != null) {
        this.calculated.bulkModulus = +K;
        if (E != null) {
          this.calculated.youngsModulus = +E;
          this.calculated.lameFirst = (3 * +K * (3 * +K - +E)) / (9 * +K - +E);
          this.calculated.shearModulus = (3 * +K * +E) / (9 * +K - +E);
          this.calculated.poissonsRatio = (3 * +K - +E) / (6 * +K);
          this.calculated.pWaveModulus =
            (3 * +K * (3 * +K + +E)) / (9 * +K - +E);
        }
        if (L != null) {
          this.calculated.youngsModulus = (9 * +K * (+K - +L)) / (3 * +K - +L);
          this.calculated.lameFirst = +L;
          this.calculated.shearModulus = (3 * +K - +L) / 2;
          this.calculated.poissonsRatio = +L / (3 * +K - +L);
          this.calculated.pWaveModulus = 3 * +K - 2 * +L;
        }
        if (G != null) {
          this.calculated.youngsModulus = (9 * +K * +G) / (3 * +K + +G);
          this.calculated.lameFirst = +K - (2 * +G) / 3;
          this.calculated.shearModulus = +G;
          this.calculated.poissonsRatio =
            (3 * +K - 2 * +G) / (2 * (3 * +K - +G));
          this.calculated.pWaveModulus = +K + (4 * +G) / 3;
        }
        if (v != null) {
          this.calculated.youngsModulus = 3 * +K * (1 - 2 * +v);
          this.calculated.lameFirst = (3 * +K * +v) / (1 + +v);
          this.calculated.shearModulus =
            (3 * +K * (1 - 2 * +v)) / (2 * (1 + +v));
          this.calculated.poissonsRatio = +v;
          this.calculated.pWaveModulus = (3 * +K * (1 - +v)) / (1 + +v);
        }
        if (M != null) {
          this.calculated.youngsModulus = (9 * +K * (+M - +K)) / (3 * +K + +M);
          this.calculated.lameFirst = (3 * +K - +M) / 2;
          this.calculated.shearModulus = (3 * (+M - +K)) / 4;
          this.calculated.poissonsRatio = (3 * +K - +M) / (3 * +K + +M);
          this.calculated.pWaveModulus = +M;
        }
      }
      if (E != null) {
        this.calculated.youngsModulus = +E;
        if (L != null) {
          const R = Math.sqrt(
            Math.pow(+E, 2) + 9 * Math.pow(+L, 2) + 2 * +E * +L
          );
          this.calculated.bulkModulus = (+E + 3 * +L + +R) / 6;
          this.calculated.lameFirst = +L;
          this.calculated.shearModulus = (+E - 3 * +L + +R) / 4;
          this.calculated.poissonsRatio = (2 * +L) / (+E + +L + +R);
          this.calculated.pWaveModulus = (+E - +L + +R) / 2;
        }
        if (G != null) {
          this.calculated.bulkModulus = (+E * +G) / (3 * (3 * +G - +E));
          this.calculated.lameFirst = (+G * (+E - 2 * +G)) / (3 * +G - +E);
          this.calculated.shearModulus = +G;
          this.calculated.poissonsRatio = +E / (2 * +G) - 1;
          this.calculated.pWaveModulus = (+G * (4 * +G - +E)) / (3 * +G - +E);
        }
        if (v != null) {
          this.calculated.bulkModulus = +E / (3 * (1 - 2 * +v));
          this.calculated.lameFirst = (+E * +v) / ((1 + +v) * (1 - 2 * +v));
          this.calculated.shearModulus = +E / (2 * (1.0 + +v));
          this.calculated.poissonsRatio = +v;
          this.calculated.pWaveModulus =
            (+E * (1 - +v)) / ((1 + +v) * (1 - 2 * +v));
        }
        if (M != null) {
          const S = Math.sqrt(
            Math.pow(+E, 2) + 9 * Math.pow(+M, 2) - 10 * +E * +M
          );
          this.calculated.bulkModulus = (3 * +M - +E + +S) / 6;
          this.calculated.lameFirst = (+M - +E + +S) / 4;
          this.calculated.shearModulus = (3 * +M + +E - +S) / 8;
          this.calculated.poissonsRatio = (+E - +M + +S) / (4 * +M);
          this.calculated.pWaveModulus = +M;
        }
      }
      if (L != null) {
        this.calculated.lameFirst = +L;
        if (G != null) {
          this.calculated.bulkModulus = +L + (2 * +G) / 3;
          this.calculated.youngsModulus = (+G * (3 * +L + 2 * +G)) / (+L * +G);
          this.calculated.shearModulus = +G;
          this.calculated.poissonsRatio = +L / (2 * (+L + +G));
          this.calculated.pWaveModulus = +L + 2 * +G;
        }
        if (v != null) {
          this.calculated.bulkModulus = (+L * (1 + v)) / (3 * +v);
          this.calculated.youngsModulus = (+L * (1 + +v) * (1 - 2 * +v)) / +v;
          this.calculated.shearModulus = (+L * (1 - 2 * +v)) / (2 * +v);
          this.calculated.poissonsRatio = +v;
          this.calculated.pWaveModulus = (+L * (1 - +v)) / +v;
        }
        if (M != null) {
          this.calculated.bulkModulus = (+M + 2 * +L) / 3;
          this.calculated.youngsModulus =
            ((+M - +L) * (+M + 2 * +L)) / (+M + +L);
          this.calculated.shearModulus = (+M - +L) / 2;
          this.calculated.poissonsRatio = +L / (+M + +L);
          this.calculated.pWaveModulus = +M;
        }
      }
      if (G != null) {
        this.calculated.shearModulus = +G;
        if (v != null) {
          this.calculated.bulkModulus =
            (2 * +G * (1 + +v)) / (3 * (1 - 2 * +v));
          this.calculated.youngsModulus = 2 * +G * (1 + +v);
          this.calculated.lameFirst = (2 * +G * +v) / (1 - 2 * +v);
          this.calculated.poissonsRatio = +v;
          this.calculated.pWaveModulus = (2 * +G * (1 - +v)) / (1 - 2 * +v);
        }
        if (M != null) {
          this.calculated.bulkModulus = +M - (4 * +G) / 3;
          this.calculated.youngsModulus = (+G * (3 * +M - 4 * +G)) / (+M - +G);
          this.calculated.lameFirst = +M - 2 * +G;
          this.calculated.poissonsRatio = (+M - 2 * +G) / (2 * +M - 2 * +G);
          this.calculated.pWaveModulus = +M;
        }
      }
      if (v != null) {
        this.calculated.poissonsRatio = +v;
        if (M != null) {
          this.calculated.bulkModulus = (+M * (1 + +v)) / (3 * (1 - +v));
          this.calculated.youngsModulus =
            (+M * (1 + +v) * (1 - 2 * +v)) / (1 - +v);
          this.calculated.lameFirst = (+M * +v) / (1 - +v);
          this.calculated.shearModulus = (+M * (1 - 2 * +v)) / (2 * (1 - +v));
          this.calculated.pWaveModulus = +M;
        }
      }
      this.calculated.bulkModulus = Number(
        this.calculated.bulkModulus
      ).toExponential();
      this.calculated.youngsModulus = Number(
        this.calculated.youngsModulus
      ).toExponential();
      this.calculated.lameFirst = Number(
        this.calculated.lameFirst
      ).toExponential();
      this.calculated.shearModulus = Number(
        this.calculated.shearModulus
      ).toExponential();
      this.calculated.pWaveModulus = Number(
        this.calculated.pWaveModulus
      ).toExponential();
    },
    resetResult() {
      this.calculated.bulkModulus = null;
      this.calculated.youngsModulus = null;
      this.calculated.lameFirst = null;
      this.calculated.shearModulus = null;
      this.calculated.poissonsRatio = null;
      this.calculated.pWaveModulus = null;
    },
    plot() {
      this.plotData[0].x = [];
      this.plotData[0].y = [];
      var n = 1000;
      var max = parseFloat(this.amplitude.max);
      var min = parseFloat(this.amplitude.min);
      var frequency = parseFloat(this.amplitude.frequency);
      var end = parseFloat(this.amplitude.end);
      for (var i = 0; i < n; i++) {
        var t = (i / (n - 1)) * end;
        this.plotData[0].x[i] = t;
        for (var j = 0; j < frequency; j++) {
          if (j == 0) {
            if (t <= (1 / frequency) * end) {
              this.plotData[0].y[i] = (t / ((1 / frequency) * end)) * max;
              break;
            }
          } else if (j % 2 != 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              this.plotData[0].y[i] =
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
              this.plotData[0].y[i] =
                min +
                ((t - (j / frequency) * end) / ((1 / frequency) * end)) *
                  (max - min);
              break;
            }
          }
        }
      }
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
        ";\n";
      for (var j = 0; j < this.amplitude.frequency; j++) {
        if (j == 0) {
          this.valueOutput +=
            "if (t <= 1 / frequency *end) \\{\n" +
            "value = (t / ((1 / frequency) * end)) * max;\n" +
            "\\}\n";
        } else if (j % 2 != 0) {
          this.valueOutput +=
            "if ((" +
            j.toString() +
            " / frequency *end < t) && (t <= (" +
            j.toString() +
            " + 1) / frequency *end)) \\{\n" +
            "value = max - ((t - (" +
            j.toString() +
            " / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n" +
            "\\}\n";
        } else if (j % 2 == 0) {
          this.valueOutput +=
            "if ((" +
            j.toString() +
            " / frequency *end < t) && (t <= (" +
            j.toString() +
            " + 1) / frequency *end)) \\{\n" +
            "value = min + ((t - (" +
            j.toString() +
            " / frequency) * end) / ((1 / frequency) * end)) * (max - min);\n" +
            "\\}\n";
        }
      }
    },
    plot2() {
      this.plotData[0].x = [];
      this.plotData[0].y = [];
      var n = 1000;
      var max = parseFloat(this.amplitude.max);
      var frequency = parseFloat(this.amplitude.frequency);
      var end = parseFloat(this.amplitude.end);
      for (var i = 0; i < n; i++) {
        var t = (i / (n - 1)) * end;
        this.plotData[0].x[i] = t;
        for (var j = 0; j < frequency; j++) {
          if (j == 0) {
            if (t <= (1 / frequency) * end) {
              this.plotData[0].y[i] = (t / end) * max * 2;
              break;
            }
          } else if (j % 2 != 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              this.plotData[0].y[i] =
                (j / frequency) * max * 2 - ((j - 1) / frequency) * max;
              break;
            }
          } else if (j % 2 == 0) {
            if (
              ((j / frequency) * end < t) &
              (t <= ((j + 1) / frequency) * end)
            ) {
              this.plotData[0].y[i] =
                ((t - ((j / 2) * end) / frequency) / end) * max * 2;
              break;
            }
          }
        }
      }
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
        ";\n";
      for (var j = 0; j < this.amplitude.frequency; j++) {
        if (j == 0) {
          this.valueOutput +=
            "if (t <= 1 / frequency *end) \\{\n" +
            "value = (t / end) * max * 2;\n" +
            "\\}\n";
        } else if (j % 2 != 0) {
          this.valueOutput +=
            "if ((" +
            j.toString() +
            " / frequency *end < t) && (t <= (" +
            j.toString() +
            " + 1) / frequency *end)) \\{\n" +
            "value = (" +
            j.toString() +
            " / frequency) * max * 2 - ((" +
            j.toString() +
            " - 1) / frequency) * max;\n" +
            "\\}\n";
        } else if (j % 2 == 0) {
          this.valueOutput +=
            "if ((" +
            j.toString() +
            " / frequency *end < t) && (t <= (" +
            j.toString() +
            " + 1) / frequency *end)) \\{\n" +
            "value = ((t - ((" +
            j.toString() +
            " / 2) * end) / frequency) / end) * max * 2;\n" +
            "\\}\n";
        }
      }
    },
    copyText(id) {
      let input = document.getElementById(id);
      input.select();
      document.execCommand("copy");
    },
    getCurrentData() {
      this.getLocalStorage("constants");
    },
    getLocalStorage(name) {
      if (localStorage.getItem(name))
        this[name] = JSON.parse(localStorage.getItem(name));
    },
  },
  mounted() {
    // console.log("mounted")
    this.getCurrentData();
    this.plot();
  },
  watch: {
    constants: {
      handler() {
        console.log("constants changed!");
        localStorage.setItem("model", JSON.stringify(this.model));
        let num = 0;
        var con = [];
        for (con in this.constants) {
          if (this.constants[con] != null) {
            num++;
          }
        }
        if (num == 2) {
          this.convert();
        }
        if (num != 2) {
          this.resetResult();
        }
        localStorage.setItem("constants", JSON.stringify(this.constants));
      },
      deep: true,
    },
    amplitude: {
      handler() {
        console.log("amplitude changed!");
        localStorage.setItem("model", JSON.stringify(this.model));
        if (this.amplitude.type == "Type 1") {
          this.plot();
        } else {
          this.plot2();
        }
        localStorage.setItem("amplitude", JSON.stringify(this.amplitude));
      },
      deep: true,
    },
  },
  created: function () {},
};
</script>
<style>
.scroll {
  height: 100%;
  overflow-y: scroll;
}
.textfield-col {
  height: 80px;
}
</style>
