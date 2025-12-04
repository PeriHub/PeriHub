// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { EventBus } from 'quasar';
import { defineBoot } from '#q-app/wrappers';

export default defineBoot(({ app }) => {
  const bus = new EventBus();

  // for Options API
  app.config.globalProperties.$bus = bus;

  // for Composition API
  app.provide('bus', bus);
});

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $bus: EventBus;
  }
}
