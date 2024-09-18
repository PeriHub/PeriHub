// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { boot } from "quasar/wrappers";
import VueChartkick from "vue-chartkick";
import "chartkick/chart.js";

export default boot(({ app }) => {
  // Set i18n instance on app
  app.use(VueChartkick);
});
