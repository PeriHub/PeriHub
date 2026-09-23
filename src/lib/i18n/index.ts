// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import i18n, { type Config } from 'sveltekit-i18n';

const config: Config = {
  loaders: [
    {
      locale: 'en-US',
      key: 'app',
      loader: async () => (await import('./en-US')).default
    }
  ]
};

export const { t, locale, locales, loading, loadTranslations } = new i18n(config);
