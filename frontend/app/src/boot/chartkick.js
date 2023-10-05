// SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { boot } from "quasar/wrappers";
import VueChartkick from "vue-chartkick";
import "chartkick/chart.js";

export default boot(({ app }) => {
  // Set i18n instance on app
  app.use(VueChartkick);
});
