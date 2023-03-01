import { defineStore } from "pinia";
import DogboneImage from "assets/models/Dogbone/Dogbone.jpg";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: "image",
    textId: "input",
    modelImg: DogboneImage,
    modelLoading: false,
    textLoading: false,
    textOutput: "",
    logOutput: "",
    bondFilterPoints: [
      {
        bondFilterPointsId: 1,
        bondFilterPointString: [],
        // bondFilterPolyString: []
      },
    ],
    filteredPointString: [1, 0, 0],
    filteredBlockIdString: [1],
    dx_value: 0.1,
  }),
  actions: {},
  resultPort: null,
  plotData: [
    {
      name: "Displacement",
      x: [1, 2, 3, 4],
      y: [10, 15, 20, 17],
      type: "scatter",
    },
  ],
});
