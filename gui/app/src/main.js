import Vue from 'vue';
import App from './App.vue';
import vuetify from './plugins/vuetify';
import VueVtkJs from 'vue-vtk-js';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faUserSecret } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { PrismEditor } from 'vue-prism-editor';
import 'vue-prism-editor/dist/prismeditor.min.css'; // import the styles
import vueNumeralFilterInstaller from 'vue-numeral-filter';
library.add(faUserSecret);
import vuescroll from "vuescroll/dist/vuescroll-native";
// import the css file 
import "vuescroll/dist/vuescroll.css";


Vue.use(vuescroll);
Vue.use(VueVtkJs);
Vue.use(vueNumeralFilterInstaller, { locale: 'en-gb' });
Vue.component('font-awesome-icon', FontAwesomeIcon);
Vue.component('PrismEditor', PrismEditor);

Vue.config.productionTip = false

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
