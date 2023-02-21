import { defineStore } from "pinia";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: 1,
    modelLoading: false,
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
