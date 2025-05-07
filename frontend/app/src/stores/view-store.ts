// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';

export const useViewStore = defineStore('view', {
  state: () => ({
    viewId: 'image',
    textId: 'input',
    modelImg: process.env.API + '/assets/images/Dogbone.jpg',
    modelLoading: false,
    textLoading: false,
    textOutput: '',
    logOutput: '',
    bondFilterPoints: [],
    filteredPointString: [1, 0, 0],
    filteredBlockIdString: [1],
    dx_value: 0.1,
    resultPort: null,
    plotData: [
      {
        name: 'Displacement',
        x: [1, 2, 3, 4],
        y: [10, 15, 20, 17],
        type: 'scatter',
      },
    ],
    plotLayout: {
      title: 'Model',
      showlegend: true,
      legend: {
        orientation: 'h',
      },
      // margin: { t: 50 },
      hovermode: 'compare',
      bargap: 0,
      xaxis: {
        showgrid: true,
        zeroline: true,
        color: 'white',
      },
      yaxis: {
        showgrid: true,
        zeroline: true,
        color: 'white',
      },
      plot_bgcolor: '#2D2D2D',
      paper_bgcolor: '#2D2D2D',
      font: {
        color: 'white',
      },
      modebar: {
        color: 'white',
        // color: "#6E6E6E"
      },
    },
  }),
  actions: {},
});
