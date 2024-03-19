// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", component: () => import("pages/LandingPage.vue") },
      { path: "/perihub", component: () => import("pages/PeriHub.vue") },
      { path: "/tools", component: () => import("pages/Tools.vue") },
      {
        path: "/publications",
        component: () => import("pages/Publications.vue"),
      },
      {
        path: "/impressum",
        component: () => import("pages/ImpressumPage.vue"),
      },
      {
        path: "/privacy",
        component: () => import("pages/PrivacyPage.vue"),
      },
      {
        path: "/copyright",
        component: () => import("pages/CopyrightPage.vue"),
      },
      {
        path: "/accessibility",
        component: () => import("pages/AccessibilityPage.vue"),
      },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
