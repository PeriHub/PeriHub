// SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from "pinia";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: "image",
    textId: "input",
    modelImg: process.env.VUE_APP_API + "/assets/models/Dogbone/Dogbone.jpg",
    modelLoading: false,
    textLoading: false,
    textOutput: "",
    logOutput: "",
    bondFilterPoints: [
    ],
    filteredPointString: [1, 0, 0],
    filteredBlockIdString: [1],
    dx_value: 0.1,
    resultPort: null,
    plotData: [
      {
        name: "Displacement",
        x: [1, 2, 3, 4],
        y: [10, 15, 20, 17],
        type: "scatter",
      },
    ],
  }),
  actions: {},
});
