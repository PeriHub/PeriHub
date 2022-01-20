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
// import vuescroll from "vuescroll/dist/vuescroll-native";
import VueCookie from 'vue-cookie';
import VueMeta from 'vue-meta'
import VueRouter from 'vue-router';
// import the css file 
// import "vuescroll/dist/vuescroll.css";
import Routes from './routes.js';

Vue.use(VueRouter);
Vue.use(VueVtkJs);
Vue.use(VueCookie);
Vue.use(VueMeta);
Vue.use(vueNumeralFilterInstaller, { locale: 'en-gb' });
Vue.component('FontAwesomeIcon', FontAwesomeIcon);
Vue.component('PrismEditor', PrismEditor);

Vue.config.productionTip = false

const router = new VueRouter({
  routes: Routes
});

new Vue({
  vuetify,
  router,
  render: h => h(App),
}).$mount('#app')

document.documentElement.style.overflow = 'hidden'