<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# Professionalizing PeriHub's frontend

This documents concrete changes made to raise the project's engineering maturity, plus a
prioritized list of further recommendations that weren't implemented (to keep this pass
scoped) but are worth doing next.

## Implemented in this pass

**Tooling that `package.json` scripts referenced but didn't actually exist:**
- `eslint.config.js` — flat config (ESLint 9) with `typescript-eslint` + `eslint-plugin-svelte`
  + `eslint-config-prettier`. The generated `src/lib/client` is excluded from linting since
  it's regenerated from the OpenAPI schema and isn't worth hand-fixing.
- `.prettierrc` / `.prettierignore` — with `prettier-plugin-svelte` and
  `prettier-plugin-tailwindcss` (the latter auto-sorts Tailwind classes, which matters once
  more than one person is touching class strings).
- `playwright.config.ts` + `test/e2e/smoke.spec.ts` — a real smoke suite (landing page,
  tools page, all 4 legal pages, 404 handling) instead of an empty test command.
- `vitest.config.ts` + `test/unit/elastic-constants.test.ts` — see "extracted pure logic"
  below.
- `.editorconfig` — consistent indentation/line-endings regardless of editor.
- Husky + lint-staged (`.husky/pre-commit`, `lint-staged` block in `package.json`) — lints
  and formats staged files before commit, so style issues never reach CI. **Note:** the
  backend already has a Python `pre-commit` (pre-commit.com) config
  (`.pre-commit-config.yaml`, scoped to `backend/`). Both tools install into the same
  `.git/hooks/pre-commit` file — whichever is `install`ed last silently overwrites the
  other's hook. `.husky/pre-commit` chains to `pre-commit run` first (if installed) so both
  can coexist regardless of install order; worth knowing about if either config changes.

**CI/CD fixes** (the existing `.github/workflows/` already had a real pipeline — these
just adapt it to the new layout and close gaps):
- `CI.yml` — updated all `./frontend/app` paths to the new root layout, and added `npm run
  lint` and `npm run check` steps before the Playwright run, so a broken build fails fast
  instead of only being caught at Docker-build time.
- `Deploy.yml` — updated the frontend Docker build context from `./frontend` to `.`.
- `dependabot.yml` — added `npm`, `docker`, and `pip` (for `backend/`) ecosystems; only
  `github-actions` was tracked before, so frontend and backend dependencies were never
  getting automated update PRs.

**REUSE/SPDX compliance** — this codebase follows the REUSE licensing standard (every file
has an SPDX header, `LICENSES/` holds the license texts). All 70+ new source files got
proper headers, plus `.license` sidecar files for JSON configs that can't hold comments.

**Extracted pure business logic out of components, with a test to prove it:**
`ConversionCard.svelte`'s elastic-constants conversion math is now
`src/lib/utils/elastic-constants.ts` — a pure function with no framework dependency — with
unit tests in `test/unit/elastic-constants.test.ts`. This is the pattern to repeat for
`SiConversionCard`, `StiffnessCard`, and the `BondFilters` geometry math: pull the math out of
`<script>`, test it directly, and let the component just handle I/O and binding. It's not
just cleaner — while extracting this one, the tests caught a **real bug that existed in the
original Vue code**: the Lamé's-first-parameter + shear-modulus branch divided by `λ·G`
where it should have divided by `λ+G` when deriving Young's modulus. Fixed, with a regression
test (`test/unit/elastic-constants.test.ts`, the "regression" test case).

## Recommended next (not implemented — prioritized)

**High priority — user-facing correctness/safety:**
1. **Form validation.** The original Quasar app had a `rules.js` (required/int/float
   validators) that never made it into this migration — none of the ~150 numeric/text inputs
   across the 14 expansion panels currently validate anything before hitting the backend.
   Recommend `sveltekit-superforms` + `zod` schemas generated from the same shapes as the
   OpenAPI client types, so client and server agree on what's valid.
2. **Replace native `<select multiple>` stand-ins.** Several panels (`Thermal.thermalModel`,
   `BoundaryConditions.stepId`, `Output.selectedOutputs`, `Deviations.parameter.id`,
   `Material.matType`) use a plain multi-select as a quick substitute for Quasar's searchable
   chip-input. Fine functionally, poor UX for lists with many options. `bits-ui` doesn't ship
   a combobox; either build one on its `Popover` + list primitives, or add `melt-ui`.
3. **Accessibility pass.** Icon-only buttons throughout (`ModelActions`, `ViewActions`,
   `Header`) use the `title` attribute for a tooltip, which is not equivalent to
   `aria-label` for screen readers. A short pass adding `aria-label` to every icon button,
   plus running `axe-core`/`svelte-check`'s a11y warnings, would close this out quickly.
4. **Finish `ModelView`/`ResultsView` (VTK.js).** Still the largest functional gap — see
   `MIGRATION.md`.

**Medium priority — maintainability:**
5. **Extract more pure logic from components**, following the `elastic-constants.ts` pattern:
   `SiConversionCard`, `StiffnessCard`, `AmplitudeCard`'s waveform generators, and
   `BondFilters`' geometry math are all good candidates and would meaningfully raise test
   coverage on the parts of this app doing real engineering calculations.
6. **Component tests**, not just e2e — `@testing-library/svelte` + Vitest for things like
   "adding a block increments blocksId correctly" across the various `add*`/`remove*`
   list-editing functions repeated in `Additive`, `Blocks`, `Damage`, `Material`, etc.
7. **Error boundaries.** A single unhandled exception in, say, `ExpansionComp` currently
   takes down the whole page. SvelteKit's `+error.svelte` at the route level, plus narrower
   boundaries around the VTK/Plotly wrappers (third-party libs are the likeliest source of
   runtime errors), would contain failures.
8. **Storybook** (or Ladle, lighter-weight) for the `ui/` primitives (`Button`, `Toggle`,
   `Select`, etc.) — useful now that there's a real design-system layer instead of
   Quasar's built-ins.

**Lower priority — polish/ops:**
9. **Error tracking** (Sentry or similar) — right now failures only surface as a `toast` and
   a `console.error`; nothing is captured for later triage.
10. **Bundle analysis** — `vite-plugin-visualizer` in CI to catch regressions, especially
    given `vtk.js` and `plotly.js` are both large. `PlotlyChart.svelte` already loads
    plotly via a dynamic `import()` inside `onMount` so it's excluded from the initial
    bundle; make sure the future VTK wrapper follows the same pattern, and confirm route-level
    code-splitting is actually keeping both out of the landing-page bundle once this is built
    for real.
11. **i18n expansion** — `sveltekit-i18n` is wired up but only has an `en-US` locale with two
    strings. If multi-language support matters, this is the place to grow it; if it doesn't,
    consider whether the i18n dependency is worth keeping at all vs. plain string constants.
12. **CONTRIBUTING.md** — the repo has issue/PR templates already
    (`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`) but no contributor guide
    covering the new stack (Svelte 5 runes conventions, where pure logic should live, the
    `npm run client` regeneration flow).
13. **Content-Security-Policy headers** in `nginx.conf` — worth adding now that the app talks
    to a configurable Keycloak/cluster URL at runtime; a strict CSP reduces the blast radius
    if a dependency (there are a lot of them: vtk.js, plotly, prismjs, jsoneditor) ever ships
    something malicious.
