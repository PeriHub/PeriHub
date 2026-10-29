import { modelStore } from './model-store.svelte';
import { parseLogProgress } from '$lib/utils/progress';
import type { BondFilters } from '$lib/client';
import { Vector3 } from 'three';

interface BondFilterPoint {
  bondFilterPointsId: number;
  bondFilterPointString: number[];
}

// A disk filter is drawn through four rim points: center + radius * normalize(normal x axis).
const AXIS_X = new Vector3(1, 0, 0);
const AXIS_Y = new Vector3(0, 1, 0);
const AXIS_X_NEG = new Vector3(-1, 0, 0);
const AXIS_Y_NEG = new Vector3(0, -1, 0);

function computeBondFilterPoints(bondFilters: BondFilters[]): BondFilterPoint[] {
  const result: BondFilterPoint[] = [];

  for (let i = 0; i < bondFilters.length; i++) {
    const bondFilterPointString: number[] = [];
    const bf = bondFilters[i]!;
    const p = (bf.params ?? {}) as Record<string, number | undefined>;
    const n = (key: string) => (typeof p[key] === 'number' ? p[key] : undefined);

    if (bf.show) {
      const normal = new Vector3(n('Normal X') ?? 0, n('Normal Y') ?? 0, n('Normal Z') ?? 0);

      if (bf.params?.['Type'] === 'Disk') {
        const cx = n('Center X'),
          cy = n('Center Y'),
          cz = n('Center Z'),
          radius = n('Radius');
        if (cx == null || cy == null || cz == null || radius == null) {
          console.log('Disk: cx, cy, cz, radius not defined');
          continue;
        }
        const center = new Vector3(cx, cy, cz);
        for (const axis of [AXIS_X, AXIS_Y, AXIS_X_NEG, AXIS_Y_NEG]) {
          const v = new Vector3().crossVectors(normal, axis).normalize();
          bondFilterPointString.push(...center.clone().addScaledVector(v, radius).toArray());
        }
      } else {
        const lx = n('Lower Left Corner X'),
          ly = n('Lower Left Corner Y'),
          lz = n('Lower Left Corner Z');
        const bx = n('Bottom Unit Vector X'),
          by = n('Bottom Unit Vector Y'),
          bz = n('Bottom Unit Vector Z');
        const bl = n('Bottom Length'),
          sl = n('Side Length');

        if (
          lx == null ||
          ly == null ||
          lz == null ||
          bx == null ||
          by == null ||
          bz == null ||
          bl == null ||
          sl == null
        ) {
          console.log('Rectangular_Plane: lx, ly, lz, bx, by, bz, bl, sl not defined');
          continue;
        }

        const bottom = new Vector3(bx, by, bz);
        const side = new Vector3().crossVectors(normal, bottom).normalize();
        const point1 = new Vector3(lx, ly, -lz);
        const point2 = point1.clone().addScaledVector(bottom.normalize(), bl);
        bondFilterPointString.push(
          ...point1.toArray(),
          ...point2.toArray(),
          ...point2.clone().addScaledVector(side, sl).toArray(),
          ...point1.clone().addScaledVector(side, sl).toArray()
        );
      }
    }

    result.push({ bondFilterPointsId: i + 1, bondFilterPointString });
  }

  return result;
}

const SCENE_BACKGROUND_KEY = 'sceneBackground';

function loadSceneBackground() {
  try {
    const saved = localStorage.getItem(SCENE_BACKGROUND_KEY);
    if (saved && /^#[0-9a-f]{6}$/i.test(saved)) return saved;
  } catch {
    // No storage (SSR, private mode) - use the default.
  }
  return '#dde1e6';
}

class ViewStore {
  viewId = $state('image');
  textId = $state('input');
  modelLoading = $state(false);
  textLoading = $state(false);
  textOutput = $state('');
  logOutput = $state('');
  // Drives the loading/error UI in LogView while the /ws log-tail socket is
  // connecting, waiting for the job's .log file to appear, or streaming it.
  // 'idle' before any job has been run this session.
  logStatus = $state<'idle' | 'waiting' | 'streaming' | 'error'>('idle');
  logStatusMessage = $state('');
  // Every visible setup section has its required fields filled in - set by
  // ExpansionComp, read by the workflow bar in ViewActions.
  setupComplete = $state(false);
  // Block / boundary condition the user is hovering or editing in the
  // setup panels - ModelPreview dims everything else.
  previewHighlight = $state<{ block?: number; bc?: string } | null>(null);
  // Last image from a model's @analysis function (ViewActions -> AnalysisView).
  // `url` is an object URL; replace it via setAnalysisImage so the old one is revoked.
  analysisImage = $state<{ label: string; url: string; filename: string } | null>(null);
  setAnalysisImage(image: { label: string; blob: Blob; filename: string } | null) {
    if (this.analysisImage) URL.revokeObjectURL(this.analysisImage.url);
    this.analysisImage = image && {
      label: image.label,
      url: URL.createObjectURL(image.blob),
      filename: image.filename
    };
  }
  // Parsed live from the streamed log text - see parseLogProgress. null
  // until PeriLab's log contains at least one recognized progress line.
  logProgress = $derived(parseLogProgress(this.logOutput));
  // Background of the 3D Model/Results scenes, remembered per browser.
  #sceneBackground = $state(loadSceneBackground());
  get sceneBackground() {
    return this.#sceneBackground;
  }
  set sceneBackground(color: string) {
    this.#sceneBackground = color;
    try {
      localStorage.setItem(SCENE_BACKGROUND_KEY, color);
    } catch {
      // Not persisted - still applies for this session.
    }
  }
  // Derived from modelStore.modelData.bondFilters - no manual mutation needed
  bondFilterPoints = $derived<BondFilterPoint[]>(
    computeBondFilterPoints(modelStore.modelData.bondFilters ?? [])
  );
}

export const viewStore = new ViewStore();
