// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { toast } from 'svelte-sonner';

export const notify = {
  positive(message: string) {
    toast.success(message);
  },
  negative(message: string) {
    toast.error(message);
  },
  info(message: string) {
    toast(message);
  },
  /** Convenience for the common `.catch((error) => notify.apiError(error))` pattern. */
  apiError(error: unknown) {
    const message =
      (error as { body?: { detail?: string } })?.body?.detail ??
      (error instanceof Error ? error.message : 'Action failed');
    toast.error(message);
  }
};
