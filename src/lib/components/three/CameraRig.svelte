<!--
SPDX-License-Identifier: Apache-2.0

Camera + OrbitControls + bounding-sphere camera fitting, shared by both
scenes (Results and Model). Must be a real child of <Canvas> since
fitToPoints() calls useThrelte()'s invalidate().
-->
<script lang="ts">
  import { T, useThrelte } from '@threlte/core';
  import { OrbitControls } from '@threlte/extras';
  import * as THREE from 'three';

  interface Props {
    // Flat [x0,y0,z0, x1,y1,z1, ...] - used only to compute the bounding
    // sphere for fitToPoints(), not rendered here.
    points: number[];
  }

  let { points }: Props = $props();

  const { invalidate } = useThrelte();

  let camera: THREE.PerspectiveCamera | undefined = $state();
  let controls: InstanceType<typeof OrbitControls> | undefined = $state();

  // One-time auto-fit the first time real geometry lands - mirrors the
  // original components' `initialCameraFit` flag. Callers that need to
  // re-fit on every reload (ModelView's viewPointData) call fitToPoints()
  // explicitly instead of relying on this.
  let hasFitCamera = $state(false);

  const box = new THREE.Box3();
  const boundingSphere = new THREE.Sphere();
  const scratchVector = new THREE.Vector3();

  function computeBoundingSphere(pts: number[]): THREE.Sphere | null {
    if (pts.length < 3) return null;
    box.makeEmpty();
    for (let i = 0; i < pts.length; i += 3) {
      scratchVector.set(pts[i], pts[i + 1], pts[i + 2]);
      box.expandByPoint(scratchVector);
    }
    box.getBoundingSphere(boundingSphere);
    return boundingSphere;
  }

  // Equivalent of vtk.js's renderer.resetCamera(): frames the camera on the
  // current point cloud's bounding sphere.
  export function fitToPoints() {
    if (!camera || !controls) return;
    const sphere = computeBoundingSphere(points);
    if (!sphere) return;

    const effectiveRadius = Math.max(sphere.radius, 0.001);
    const fovRadians = (camera.fov * Math.PI) / 180;
    const distance = (effectiveRadius / Math.sin(fovRadians / 2)) * 1.3;

    const direction = new THREE.Vector3(0, 0, 1).normalize();
    camera.position.copy(sphere.center).addScaledVector(direction, distance);
    camera.near = Math.max(distance / 100, 0.01);
    camera.far = distance * 100;
    camera.updateProjectionMatrix();

    controls.target.copy(sphere.center);
    controls.update();
    invalidate();
  }

  export function resetCamera() {
    fitToPoints();
  }

  $effect(() => {
    if (hasFitCamera || !camera || !controls || points.length === 0) return;
    hasFitCamera = true;
    fitToPoints();
  });
</script>

<T.PerspectiveCamera makeDefault position={[5, 5, 5]} fov={50} near={0.01} far={1000} bind:ref={camera}>
  <OrbitControls bind:ref={controls} enableDamping dampingFactor={0.1} />
</T.PerspectiveCamera>
