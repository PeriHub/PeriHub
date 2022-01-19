import LandingPage from './components/LandingPage.vue';
import PeriHub from './components/PeriHub.vue';
import Guide from './components/Guide.vue';
import Examples from './components/guides/Examples.vue';
import Dogbone from './components/guides/examples/Dogbone.vue';
import GIICmodel from './components/guides/examples/GIICmodel.vue';
import DCBmodel from './components/guides/examples/DCBmodel.vue';
import FeFiles from './components/guides/examples/FeFiles.vue';
import GettingStarted from './components/guides/GettingStarted.vue';
import Introduction from './components/guides/Introduction.vue';
import Publications from './components/Publications.vue';

export default [
  // Redirects to /route-one as the default route.
  // {
  //   path: '/',
  //   redirect: '/landingPage'
  // },
  {
    path: '/',
    components: {a: LandingPage}
  },
  {
    path: '/perihub',
    components: {a: PeriHub}
  },
  {
    path: '/guide',
    redirect: '/guide/introduction',
    components: {a: Guide},
    children: [
      {
          path: 'introduction',
          components: {b: Introduction}
      },
      {
          path: 'examples',
          components: {b: Examples},
          children: [
            {
                path: 'dogbone',
                components: {c: Dogbone}
            },
            {
                path: 'giicmodel',
                components: {c: GIICmodel}
            },
            {
                path: 'dcbmodel',
                components: {c: DCBmodel}
            },
            {
                path: 'fefiles',
                components: {c: FeFiles}
            }
          ]
      },
      {
          path: 'gettingStarted',
          components: {b: GettingStarted}
      }
    ]
  },
  {
    path: '/publications',
    components: {a: Publications}
  },
];