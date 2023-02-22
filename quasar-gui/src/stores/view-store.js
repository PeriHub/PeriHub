import { defineStore } from "pinia";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: 0,
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
  }),
  actions: {},
});
