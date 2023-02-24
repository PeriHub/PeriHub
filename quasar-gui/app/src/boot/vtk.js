import { boot } from "quasar/wrappers";
import * as VTK from "vue-vtk-js";

export default boot(({ app }) => {
  app.use(VTK);
});
