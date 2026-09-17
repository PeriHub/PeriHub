// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import mitt from 'mitt';

export type AppEvents = {
  resetData: void;
};

export const bus = mitt<AppEvents>();
