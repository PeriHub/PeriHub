// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { boot } from "quasar/wrappers";
import * as VTK from "vue-vtk-js";

export default boot(({ app }) => {
  app.use(VTK);
});
