import LandingPage from './components/LandingPage.vue';
import Home from './components/Home.vue';
import Guide from './components/Guide.vue';
import Examples from './components/guides/Examples.vue';
import GettingStarted from './components/guides/GettingStarted.vue';
import Introduction from './components/guides/Introduction.vue';
import Publications from './components/Publications.vue';

export default [
  // Redirects to /route-one as the default route.
  {
    path: '/',
    redirect: '/landingPage'
  },
  {
    path: '/landingPage',
    components: {a: LandingPage}
  },
  {
    path: '/home',
    components: {a: Home}
  },
  {
    path: '/guide',
    components: {a: Guide},
    children: [,
        {
            path: 'introduction',
            components: {b: Introduction}
        },
        {
            path: 'examples',
            components: {b: Examples}
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