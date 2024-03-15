// SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import IntroductionPage from "pages/guide/IntroductionPage.vue";
import GettingStartedPage from "pages/guide/GettingStartedPage.vue";

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
  {
    path: "/guide",
    component: () => import("layouts/GuideLayout.vue"),
    children: [
      { path: "/guide/Introduction", component: () => import("pages/guide/IntroductionPage.vue") },
      { path: "/guide/GettingStarted", component: () => import("pages/guide/GettingStartedPage.vue") },
      { path: "/guide/Buttons", component: () => import("pages/guide/ButtonPage.vue") },
      { path: "/guide/Output", component: () => import("pages/guide/OutputPage.vue") },
      { path: "/guide/faq", component: () => import("pages/guide/FaqPage.vue") },
    ],
  },
  { path: "/guide", redirect: "/guide/Introduction" },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
