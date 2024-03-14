<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div class="legend" ref="legend">
    <span v-for="(value, index) in  values " :key="index"
      :style="{ bottom: (((index - 0.5) / (values.length - 1)) * 100) + '%', left: '15px' }">&#8213; {{ value }}</span>
  </div>
</template>

<script>
export default {
  name: 'VerticalColoredLegend',
  props: {
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      required: true
    },
    numValues: {
      type: Number,
      default: 11
    }
  },
  data() {
    return {
      values: []
    };
  },
  mounted() {
    this.generateValues();
  },
  methods: {
    generateValues() {
      const interval = (this.max - this.min) / (this.numValues - 1);

      for (let i = 0; i < this.numValues; i++) {
        const value = this.min + i * interval;
        this.values.push(value.toExponential(2));
      }
    }
  }
};
</script>

<style scoped>
.legend {
  background: linear-gradient(to bottom, #ec3c3f, #fb8620, #f3b500, #ded302, #bae216, #7fe345, #41da8a, #14c6c7, #21a1e7, #3f72f0, #5125ee);
  /* Define your gradient colors */
  width: 20px;
  /* Adjust width as needed */
  height: 150px;
  /* Adjust height as needed */
  position: relative;
  display: inline-block;
  margin-right: 20px;
  /* Adjust margin as needed */
}

.legend span {
  position: absolute;
  color: #fff;
  font-size: 12px;
  font-family: Arial, sans-serif;
  white-space: nowrap;
}
</style>
