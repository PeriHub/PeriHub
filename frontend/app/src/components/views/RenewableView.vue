<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <line-chart :data=plot_data></line-chart>
</template>

<script>
    import { defineComponent } from 'vue'
    import { useViewStore } from 'stores/view-store';
    import axios from 'axios';
    export default defineComponent({
        name: 'RenewableView',
        setup() {
            const viewStore = useViewStore();

            return {
                viewStore,
            }
        },
        data() {
            return {
                // data: {'2017-01-01 00:00:00 -0800': 2, '2017-01-01 00:01:00 -0800': 5}
                plot_data: {}
            };
        },
        methods: {},
        async mounted() {
          // let raw_data =[
          //   {
          //     "name": {
          //       "en": "Renewable Share of Load"
          //     },
          //     "data": [
          //       88.1,
          //       88.4,
          //       89.1,
          //       89.2,
          //       89.2
          //     ],
          //     "xAxisValues": [
          //       1696370400000,
          //       1696371300000,
          //       1696372200000,
          //       1696373100000,
          //       1696374000000
          //     ],
          //     "xAxisFormat": "unixTime",
          //     "date": 1696426228018
          //   },
          //   {
          //     "name": {
          //       "en": "Color"
          //     },
          //     "comment": "0: Red, 1: Yellow, 2: Green",
          //     "data": [
          //       2,
          //       2,
          //       2,
          //       2,
          //       2
          //     ]
          //   }
          // ]

          const response = await axios.get('https://api.energy-charts.info/traffic_signal', {
            params: {
              'country': 'de'
            }
          });

          let raw_data = response.data
          // Initialize an empty result object
          let data = {};

          // Loop through the xAxisValues and data arrays
          raw_data[0].data.forEach((value, index) => {
              // Convert the timestamp to a date string
              let timestamp = raw_data[0].xAxisValues[index];
              // console.log(timestamp)
              let date = new Date(timestamp);
               // Extract date components
              let year = date.getFullYear();
              let month = (date.getMonth() + 1).toString().padStart(2, '0');
              let day = date.getDate().toString().padStart(2, '0');
              let hours = date.getHours().toString().padStart(2, '0');
              let minutes = date.getMinutes().toString().padStart(2, '0');
              let seconds = date.getSeconds().toString().padStart(2, '0');

              // Create a date string with date, hours, minutes, and seconds
              let dateString = `${year}-${month}-${day} ${hours}:${minutes}:${seconds} -0800`;

              // Assign the value to the result object with the date string as the key
              data[dateString] = value;
          });
          this.plot_data = data;
          console.log(this.plot_data);

        }
    })
</script>

<style></style>
