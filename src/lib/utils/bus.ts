// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export type AppEvents = {
  resetData: void;
  openHidePanels: void;
  showTutorial: void;
};

type Handler<T> = (payload: T) => void;
const handlers = new Map<keyof AppEvents, Set<Handler<never>>>();

export const bus = {
  on<K extends keyof AppEvents>(type: K, handler: Handler<AppEvents[K]>) {
    if (!handlers.has(type)) handlers.set(type, new Set());
    handlers.get(type)!.add(handler as Handler<never>);
  },
  off<K extends keyof AppEvents>(type: K, handler: Handler<AppEvents[K]>) {
    handlers.get(type)?.delete(handler as Handler<never>);
  },
  emit<K extends keyof AppEvents>(type: K, payload?: AppEvents[K]) {
    handlers
      .get(type)
      ?.forEach((handler) => (handler as Handler<AppEvents[K] | undefined>)(payload));
  }
};
