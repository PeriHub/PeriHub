import { boot } from "quasar/wrappers";
import VTK from "vue-vtk-js";

export default boot(({ app }) => {
  app.use(VTK);
});
