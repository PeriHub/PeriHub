// SPDX-FileCopyrightText: 2023 Razvan Stoenescu
//
// SPDX-License-Identifier: MIT

/* eslint-disable */

module.exports = api => {
  return {
    presets: [
      [
        '@quasar/babel-preset-app',
        api.caller(caller => caller && caller.target === 'node')
          ? { targets: { node: 'current' } }
          : {}
      ]
    ]
  }
}
