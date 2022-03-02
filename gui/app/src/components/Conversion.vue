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
    </div>
  </v-container>
</template>

<script>
import axios from "axios";
import bibtexParse from "bibtex-parse-js";
// import bibFile from '../static/test.bib'

export default {
  components: {
    bibtexParse,
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
    };
  },
  methods: {
    convert() {
      const K = this.constants.bulkModulus;
      const E = this.constants.youngsModulus;
      const L = this.constants.lameFirst;
      const G = this.constants.shearModulus;
      const v = this.constants.poissonsRatio;
      const M = this.constants.pWaveModulus;
      if (K != null) {
        this.calculated.bulkModulus = K;
        if (E != null) {
          this.calculated.youngsModulus = E;
          this.calculated.lameFirst = (3 * K * (3 * K - E)) / (9 * K - E);
          this.calculated.shearModulus = (3 * K * E) / (9 * K - E);
          this.calculated.poissonsRatio = (3 * K - E) / (6 * K);
          this.calculated.pWaveModulus = (3 * K * (3 * K + E)) / (9 * K - E);
        }
        if (L != null) {
          this.calculated.youngsModulus = (9 * K * (K - L)) / (3 * K - L);
          this.calculated.lameFirst = L;
          this.calculated.shearModulus = (3 * K - L) / 2;
          this.calculated.poissonsRatio = L / (3 * K - L);
          this.calculated.pWaveModulus = 3 * K - 2 * L;
        }
        if (G != null) {
          this.calculated.youngsModulus = (9 * K * G) / (3 * K + G);
          this.calculated.lameFirst = K - (2 * G) / 3;
          this.calculated.shearModulus = G;
          this.calculated.poissonsRatio = (3 * K - 2 * G) / (2 * (3 * K - G));
          this.calculated.pWaveModulus = K + (4 * G) / 3;
        }
        if (v != null) {
          this.calculated.youngsModulus = 3 * K * (1 - 2 * v);
          this.calculated.lameFirst = (3 * K * v) / (1 + v);
          this.calculated.shearModulus = (3 * K * (1 - 2 * v)) / (2 * (1 + v));
          this.calculated.poissonsRatio = v;
          this.calculated.pWaveModulus = (3 * K * (1 - v)) / (1 + v);
        }
        if (M != null) {
          this.calculated.youngsModulus = (9 * K * (M - K)) / (3 * K + M);
          this.calculated.lameFirst = (3 * K - M) / 2;
          this.calculated.shearModulus = (3 * (M - K)) / 4;
          this.calculated.poissonsRatio = (3 * K - M) / (3 * K + M);
          this.calculated.pWaveModulus = M;
        }
      }
      if (E != null) {
        this.calculated.youngsModulus = E;
        if (L != null) {
          const R = Math.sqrt(Math.pow(E, 2) + 9 * Math.pow(L, 2) + 2 * E * L);
          this.calculated.bulkModulus = (E + 3 * L + R) / 6;
          this.calculated.lameFirst = L;
          this.calculated.shearModulus = (E - 3 * L + R) / 4;
          this.calculated.poissonsRatio = (2 * L) / (E + L + R);
          this.calculated.pWaveModulus = (E - L + R) / 2;
        }
        if (G != null) {
          this.calculated.bulkModulus = (E * G) / (3 * (3 * G - E));
          this.calculated.lameFirst = (G * (E - 2 * G)) / (3 * G - E);
          this.calculated.shearModulus = G;
          this.calculated.poissonsRatio = E / (2 * G) - 1;
          this.calculated.pWaveModulus = (G * (4 * G - E)) / (3 * G - E);
        }
        if (v != null) {
          this.calculated.bulkModulus = E / (3 * (1 - 2 * v));
          this.calculated.lameFirst = (E * v) / ((1 + v) * (1 - 2 * v));
          this.calculated.shearModulus = E / (2 * (1 + v));
          this.calculated.poissonsRatio = v;
          this.calculated.pWaveModulus =
            (E * (1 - v)) / ((1 + v) * (1 - 2 * v));
        }
        if (M != null) {
          const S = Math.sqrt(Math.pow(E, 2) + 9 * Math.pow(M, 2) - 10 * E * M);
          this.calculated.bulkModulus = (3 * M - E + S) / 6;
          this.calculated.lameFirst = (M - E + S) / 4;
          this.calculated.shearModulus = (3 * M + E - S) / 8;
          this.calculated.poissonsRatio = (E - M + S) / (4 * M);
          this.calculated.pWaveModulus = M;
        }
      }
      if (L != null) {
        this.calculated.lameFirst = L;
        if (G != null) {
          this.calculated.bulkModulus = L + (2 * G) / 3;
          this.calculated.youngsModulus = (G * (3 * L + 2 * G)) / (L * G);
          this.calculated.shearModulus = G;
          this.calculated.poissonsRatio = L / (2 * (L + G));
          this.calculated.pWaveModulus = L + 2 * G;
        }
        if (v != null) {
          this.calculated.bulkModulus = (L * (1 + v)) / (3 * v);
          this.calculated.youngsModulus = (L * (1 + v) * (1 - 2 * v)) / v;
          this.calculated.shearModulus = (L * (1 - 2 * v)) / (2 * v);
          this.calculated.poissonsRatio = v;
          this.calculated.pWaveModulus = (L * (1 - v)) / v;
        }
        if (M != null) {
          this.calculated.bulkModulus = (M + 2 * L) / 3;
          this.calculated.youngsModulus = ((M - L) * (M + 2 * L)) / (M + L);
          this.calculated.shearModulus = (M - L) / 2;
          this.calculated.poissonsRatio = L / (M + L);
          this.calculated.pWaveModulus = M;
        }
      }
      if (G != null) {
        this.calculated.shearModulus = G;
        if (v != null) {
          this.calculated.bulkModulus = (2 * G * (1 + v)) / (3 * (1 - 2 * v));
          this.calculated.youngsModulus = 2 * G * (1 + v);
          this.calculated.lameFirst = (2 * G * v) / (1 - 2 * v);
          this.calculated.poissonsRatio = v;
          this.calculated.pWaveModulus = (2 * G * (1 - v)) / (1 - 2 * v);
        }
        if (M != null) {
          this.calculated.bulkModulus = M - (4 * G) / 3;
          this.calculated.youngsModulus = (G * (3 * M - 4 * G)) / (M - G);
          this.calculated.lameFirst = M - 2 * G;
          this.calculated.poissonsRatio = (M - 2 * G) / (2 * M - 2 * G);
          this.calculated.pWaveModulus = M;
        }
      }
      if (v != null) {
        this.calculated.poissonsRatio = v;
        if (M != null) {
          this.calculated.bulkModulus = (M * (1 + v)) / (3 * (1 - v));
          this.calculated.youngsModulus = (M * (1 + v) * (1 - 2 * v)) / (1 - v);
          this.calculated.lameFirst = (M * v) / (1 - v);
          this.calculated.shearModulus = (M * (1 - 2 * v)) / (2 * (1 - v));
          this.calculated.pWaveModulus = M;
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
