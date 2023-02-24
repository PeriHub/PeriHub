import { defineStore } from "pinia";
import DogboneImage from "assets/models/Dogbone/Dogbone.jpg";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: 0,
    modelImg: DogboneImage,
    modelLoading: false,
    textLoading: false,
    textOutput: "",
    bondFilterPoints: [
      {
        bondFilterPointsId: 1,
        bondFilterPointString: [],
        // bondFilterPolyString: []
      },
    ],
    dx_value: 0.1,
  }),
  actions: {},
});
