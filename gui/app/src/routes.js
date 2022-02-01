import LandingPage from './components/LandingPage.vue';
import PeriHub from './components/PeriHub.vue';
import Guide from './components/Guide.vue';
import Input from './components/guides/Input.vue';
import Model from './components/guides/input/Model.vue';
import Material from './components/guides/input/Material.vue';
import DamageModels from './components/guides/input/DamageModels.vue';
import Blocks from './components/guides/input/Blocks.vue';
import BoundaryConditions from './components/guides/input/BoundaryConditions.vue';
import IOutput from './components/guides/input/Output.vue';
import Solver from './components/guides/input/Solver.vue';
import Job from './components/guides/input/Job.vue';
import Output from './components/guides/Output.vue';
import Modelview from './components/guides/output/Modelview.vue';
import Textview from './components/guides/output/Textview.vue';
import Examples from './components/guides/Examples.vue';
import Dogbone from './components/guides/examples/Dogbone.vue';
import GIICmodel from './components/guides/examples/GIICmodel.vue';
import DCBmodel from './components/guides/examples/DCBmodel.vue';
import FeFiles from './components/guides/examples/FeFiles.vue';
import GettingStarted from './components/guides/GettingStarted.vue';
import Introduction from './components/guides/Introduction.vue';
import Buttons from './components/guides/Buttons.vue';
import FAQ from './components/guides/FAQ.vue';
import Publications from './components/Publications.vue';
import Conversion from './components/Conversion.vue';

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
          path: 'buttons',
          components: {b: Buttons}
      },
      {
          path: 'faq',
          components: {b: FAQ}
      },
      {
          path: 'input',
          components: {b: Input},
          children: [
            {
                path: 'model',
                components: {c: Model}
            },
            {
                path: 'material',
                components: {c: Material}
            },
            {
                path: 'damageModels',
                components: {c: DamageModels}
            },
            {
                path: 'blocks',
                components: {c: Blocks}
            },
            {
                path: 'boundaryConditions',
                components: {c: BoundaryConditions}
            },
            {
                path: 'output',
                components: {c: IOutput}
            },
            {
                path: 'solver',
                components: {c: Solver}
            },
            {
                path: 'job',
                components: {c: Job}
            }
          ]
      },
      {
          path: 'output',
          components: {b: Output},
          children: [
            {
                path: 'modelview',
                components: {c: Modelview}
            },
            {
                path: 'textview',
                components: {c: Textview}
            }
          ]
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
  {
    path: '/conversion',
    components: {a: Conversion}
  },
];