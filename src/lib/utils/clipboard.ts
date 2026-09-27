// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { notify } from './notify';

export async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    notify.info('Copied to clipboard');
  } catch {
    notify.negative('Could not copy — select the value and copy it manually');
  }
}
