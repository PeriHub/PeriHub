const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", component: () => import("pages/LandingPage.vue") },
      { path: "/perihub", component: () => import("pages/PeriHub.vue") },
      {
        path: "/guide",
        component: () => import("pages/GuidePage.vue"),
        // children: [
        //   { path: "/introduction", component: () => import("pages/LandingPage.vue") },
        //   { path: "/buttons", component: () => import("pages/PeriHub.vue") },
        //   { path: "/faq", component: () => import("pages/GuidePage.vue") },
        // ],
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
