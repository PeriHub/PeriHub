// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { viewStore } from '$lib/stores/view-store.svelte';

type Target = NonNullable<typeof viewStore.previewHighlight>;

/** Spread onto a setup-panel row so hovering or editing it highlights `target` in ModelPreview. */
export function previewHighlight(target: () => Target) {
  const set = () => (viewStore.previewHighlight = target());
  const clear = () => (viewStore.previewHighlight = null);
  return { onpointerenter: set, onpointerleave: clear, onfocusin: set, onfocusout: clear };
}
