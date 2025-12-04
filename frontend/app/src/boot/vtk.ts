// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineBoot } from '#q-app/wrappers';
// @ts-expect-error Bla
import * as VTK from 'vue-vtk-js';

export default defineBoot(({ app }) => {
  app.use(VTK);
});
