// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { EventBus } from 'quasar'
import { boot } from 'quasar/wrappers'

export default boot(({ app }) => {
  const bus = new EventBus()

  // for Options API
  app.config.globalProperties.$bus = bus

  // for Composition API
  app.provide('bus', bus)
})