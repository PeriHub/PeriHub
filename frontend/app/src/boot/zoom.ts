// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { boot } from "quasar/wrappers";
// @ts-expect-error Bla
import VueImageZoomer from "vue-image-zoomer";
import "vue-image-zoomer/dist/style.css";

export default boot(({ app }) => {
  app.use(VueImageZoomer);
});
