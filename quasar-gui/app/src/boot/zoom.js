import { boot } from "quasar/wrappers";
import VueImageZoomer from 'vue-image-zoomer'
import 'vue-image-zoomer/dist/style.css';

export default boot(({ app }) => {
  app.use(VueImageZoomer);
});
