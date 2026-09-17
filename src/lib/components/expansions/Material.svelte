<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { inv, matrix } from 'mathjs';
  import { Plus, Trash2, Upload } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { uploadFiles as uploadFilesApi } from '$lib/client';
  import type { Material, properties as MaterialProperties } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const materials = $derived(modelStore.modelData.materials ?? []);
  const materialModelNames = [
    'Bond-based Elastic', 'PD Solid Elastic', 'PD Solid Plastic', 'Correspondence Elastic', 'Correspondence Plastic'
  ];
  const materialSymmetries = ['Isotropic', 'Anisotropic', 'Orthotropic', 'Transverse Isotropic'];
  const stabilizationTypes = ['Bond Based', 'State Based', 'Sub Horizon', 'Global Stiffness'];

  let multiSoInput: HTMLInputElement;
  let propsInput: HTMLInputElement;
  let selectedMaterial = 0;

  function editNumStateVars(numStateVars: number) {
    bus.emit('addStateVarsToOutput' as never, numStateVars as never);
  }

  function calculateStiffnessMatrix(materialId: number) {
    const material = materials[materialId]!;
    const sm = material.stiffnessMatrix;
    if (!sm?.calculateStiffnessMatrix) return;

    const E1 = sm.engineeringConstants.E1 as number | null;
    const E2 = sm.engineeringConstants.E2 as number | null;
    let E3 = sm.engineeringConstants.E3 as number | null;
    const G12 = sm.engineeringConstants.G12 as number | null;
    let G13 = sm.engineeringConstants.G13 as number | null;
    let G23 = sm.engineeringConstants.G23 as number | null;
    const nu12 = sm.engineeringConstants.nu12 as number | null;
    let nu13 = sm.engineeringConstants.nu13 as number | null;
    let nu23 = sm.engineeringConstants.nu23 as number | null;

    if (E1 == null || E2 == null || G12 == null || nu12 == null) return;

    if (E3 == null) E3 = E2;
    if (G13 == null) G13 = G12;
    if (nu13 == null) nu13 = nu12;
    if (nu23 == null) nu23 = nu12;
    if (G23 == null) G23 = E2 / (2 * (1 + nu23));

    const compliance = matrix([
      [1 / E1, -nu12 / E1, -nu13 / E1, 0, 0, 0],
      [-nu12 / E1, 1 / E2, -nu23 / E2, 0, 0, 0],
      [-nu13 / E1, -nu23 / E2, 1 / E3, 0, 0, 0],
      [0, 0, 0, 1 / G23, 0, 0],
      [0, 0, 0, 0, 1 / G13, 0],
      [0, 0, 0, 0, 0, 1 / G12]
    ]);
    const s = inv(compliance).toArray() as number[][];

    sm.matrix = {
      C11: s[0]![0]!, C12: s[0]![1]!, C13: s[0]![2]!, C14: s[0]![3]!, C15: s[0]![4]!, C16: s[0]![5]!,
      C22: s[1]![1]!, C23: s[1]![2]!, C24: s[1]![3]!, C25: s[1]![4]!, C26: s[1]![5]!,
      C33: s[2]![2]!, C34: s[2]![3]!, C35: s[2]![4]!, C36: s[2]![5]!,
      C44: s[3]![3]!, C45: s[3]![4]!, C46: s[3]![5]!,
      C55: s[4]![4]!, C56: s[4]![5]!,
      C66: s[5]![5]!
    };
  }

  function uploadSo() {
    multiSoInput.click();
  }

  function onMultiFilePicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (!files || files.length === 0) return;
    viewStore.modelLoading = true;

    const formData = new FormData();
    Array.from(files).forEach((f) => formData.append('files', f));

    uploadFilesApi({
      modelName: modelStore.selectedModel.title,
      modelFolderName: modelStore.modelData.model.modelFolderName,
      formData
    } as never)
      .then(() => notify.positive('File uploaded'))
      .catch((error) => notify.apiError(error));

    viewStore.modelLoading = false;
  }

  function uploadProps(id: number) {
    propsInput.click();
    selectedMaterial = id;
  }

  function onPropsFilePicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (!files || files.length === 0) return;

    const fr = new FileReader();
    fr.onload = (e) => {
      const inputString = e.target?.result as string;
      const filteredString = inputString.match(/\*User([\D\S]*?)\*/gi);
      if (!filteredString) return;

      let propsArray = filteredString[0]!.split(/[\n,]/gi).filter((v) => v.trim() !== '');
      propsArray = propsArray.slice(0, propsArray.length - 1);
      const numConstants = propsArray.length - 2;

      if (!propsArray[1]) {
        console.log('Constants not found.');
        return;
      }
      const numConstantsFound = propsArray[1].match(/\d+/);
      if (!numConstantsFound) {
        console.log('Number of constants not found.');
        return;
      }

      if (parseFloat(numConstantsFound[0]!) === numConstants) {
        materials[0]!.properties = [];
        const parameterString = inputString.match(/\*PARAMETER([\D\S]*?)\*HEADING/gi);
        if (!parameterString) {
          console.log('Parameter string not found.');
          return;
        }
        const parameterValues = parameterString[0]!.match(/\w+=([\d.]+)/gi);
        if (!parameterValues) {
          console.log('Parameter values not found.');
          return;
        }

        for (let i = 2; i < propsArray.length; i++) {
          addProp(0);
          let propValue = propsArray[i]!.trim();
          if (propValue.startsWith('<') && propValue.endsWith('>')) {
            const paramName = propValue.slice(1, -1);
            const paramValue = parameterValues.find((p) => p.startsWith(`${paramName}=`));
            if (paramValue) propValue = paramValue.split('=')[1]!;
            else console.log(`Parameter ${paramName} not found.`);
          }
          materials[0]!.properties![i - 2]!.value = parseFloat(propValue);
        }
      } else {
        console.log('Length of Propsarray unexpected');
      }
    };
    fr.readAsText(files.item(0)!);
  }

  function addMaterial() {
    if (!modelStore.modelData.materials) modelStore.modelData.materials = [];
    const list = modelStore.modelData.materials;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Material) : ({} as Material);
    newItem.materialsId = len + 1;
    newItem.name = `Material ${len + 1}`;
    list.push(newItem);
  }

  function removeMaterial(index: number) {
    materials.splice(index, 1);
    materials.forEach((m, i) => (m.materialsId = i + 1));
  }

  function addProp(index: number) {
    const material = materials[index]!;
    if (!material.properties) material.properties = [];
    const len = material.properties.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(material.properties[len - 1])) as MaterialProperties)
        : ({} as MaterialProperties);
    newItem.materialsPropId = len + 1;
    newItem.name = `Prop_${len + 1}`;
    material.properties.push(newItem);
  }

  function removeProp(index: number, subindex: number) {
    materials[index]!.properties!.splice(subindex, 1);
  }
</script>

<div class="space-y-3 p-3">
  {#each materials as material, index (material.materialsId ?? index)}
    <div class="space-y-3 rounded-md border border-border p-3">
      <h4 class="font-medium">Material {material.materialsId}</h4>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`mat-name-${index}`}>name</Label>
          <Input id={`mat-name-${index}`} bind:value={material.name} />
        </div>
        <Button variant="ghost" size="icon" onclick={() => removeMaterial(index)} title="Remove Material">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="w-64 space-y-1">
        <Label for={`mat-type-${index}`}>Material Models</Label>
        <select
          id={`mat-type-${index}`}
          multiple
          bind:value={material.matType}
          class="h-24 w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
        >
          {#each materialModelNames as name (name)}
            <option value={name}>{name}</option>
          {/each}
        </select>
      </div>

      {#if material.matType?.includes('User')}
        <div class="space-y-2 border-t border-border pt-2">
          {#each material.properties ?? [] as prop, subindex (prop.materialsPropId ?? subindex)}
            <div class="flex flex-wrap items-end gap-3">
              <div class="space-y-1">
                <Label for={`mat-prop-${index}-${subindex}`}>{prop.name}</Label>
                <Input id={`mat-prop-${index}-${subindex}`} type="number" bind:value={prop.value} />
              </div>
              <Button variant="ghost" size="icon" onclick={() => removeProp(index, subindex)} title="Remove Property">
                <Trash2 class="h-4 w-4" />
              </Button>
            </div>
          {/each}
          <div class="flex flex-wrap items-end gap-2">
            <Button variant="outline" size="sm" onclick={() => addProp(index)}>
              <Plus class="h-4 w-4" /> Add Property
            </Button>
            <Button variant="outline" size="sm" onclick={() => uploadProps(index)}>
              <Upload class="h-4 w-4" /> Upload Property
            </Button>
            <Button variant="outline" size="sm" onclick={uploadSo}>
              <Upload class="h-4 w-4" /> Upload shared Library
            </Button>
            <div class="space-y-1">
              <Label for={`mat-nsv-${index}`}>Number of State Vars</Label>
              <Input
                id={`mat-nsv-${index}`}
                type="number"
                bind:value={material.numStateVars}
                oninput={() => editNumStateVars(material.numStateVars!)}
              />
            </div>
          </div>
        </div>
      {/if}

      {#if material.materialSymmetry === 'Isotropic'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`mat-pr-${index}`}>Poisson's Ratio</Label>
            <Input id={`mat-pr-${index}`} type="number" bind:value={material.poissonsRatio} />
          </div>
          <div class="space-y-1">
            <Label for={`mat-bulk-${index}`}>Bulk Modulus</Label>
            <Input id={`mat-bulk-${index}`} type="number" bind:value={material.bulkModulus} />
          </div>
          <div class="space-y-1">
            <Label for={`mat-shear-${index}`}>Shear Modulus</Label>
            <Input id={`mat-shear-${index}`} type="number" bind:value={material.shearModulus} />
          </div>
          <div class="space-y-1">
            <Label for={`mat-young-${index}`}>Young's Modulus</Label>
            <Input id={`mat-young-${index}`} type="number" bind:value={material.youngsModulus} />
          </div>
        </div>
      {/if}

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`mat-sym-${index}`}>Material Symmetry</Label>
          <select
            id={`mat-sym-${index}`}
            bind:value={material.materialSymmetry}
            class="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
          >
            {#each materialSymmetries as sym (sym)}
              <option value={sym}>{sym}</option>
            {/each}
          </select>
        </div>
        <Toggle bind:checked={material.planeStress} label="Plane Stress" />
        <Toggle bind:checked={material.planeStrain} label="Plane Strain" />
        {#if material.stiffnessMatrix && material.materialSymmetry === 'Anisotropic' && material.matType?.includes('Correspondence')}
          <Toggle bind:checked={material.stiffnessMatrix.calculateStiffnessMatrix} label="Calculate Stiffness Matrix" />
        {/if}
      </div>

      {#if material.materialSymmetry === 'Transverse Isotropic' || material.materialSymmetry === 'Orthotropic'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`mat-ex-${index}`}>Young's Modulus X</Label>
            <Input id={`mat-ex-${index}`} type="number" bind:value={material.youngsModulusX} />
          </div>
          <div class="space-y-1">
            <Label for={`mat-ey-${index}`}>Young's Modulus Y</Label>
            <Input id={`mat-ey-${index}`} type="number" bind:value={material.youngsModulusY} />
          </div>
          {#if material.materialSymmetry === 'Orthotropic'}
            <div class="space-y-1">
              <Label for={`mat-ez-${index}`}>Young's Modulus Z</Label>
              <Input id={`mat-ez-${index}`} type="number" bind:value={material.youngsModulusZ} />
            </div>
          {/if}
          <div class="space-y-1">
            <Label for={`mat-pxy-${index}`}>Poisson's Ratio XY</Label>
            <Input id={`mat-pxy-${index}`} type="number" bind:value={material.poissonsRatioXY} />
          </div>
          {#if material.planeStrain || material.materialSymmetry === 'Orthotropic'}
            <div class="space-y-1">
              <Label for={`mat-pyz-${index}`}>Poisson's Ratio YZ</Label>
              <Input id={`mat-pyz-${index}`} type="number" bind:value={material.poissonsRatioYZ} />
            </div>
          {/if}
          {#if material.materialSymmetry === 'Orthotropic'}
            <div class="space-y-1">
              <Label for={`mat-pxz-${index}`}>Poisson's Ratio XZ</Label>
              <Input id={`mat-pxz-${index}`} type="number" bind:value={material.poissonsRatioXZ} />
            </div>
          {/if}
          <div class="space-y-1">
            <Label for={`mat-gxy-${index}`}>Shear Modulus XY</Label>
            <Input id={`mat-gxy-${index}`} type="number" bind:value={material.shearModulusXY} />
          </div>
          {#if material.materialSymmetry === 'Orthotropic'}
            <div class="space-y-1">
              <Label for={`mat-gyz-${index}`}>Shear Modulus YZ</Label>
              <Input id={`mat-gyz-${index}`} type="number" bind:value={material.shearModulusYZ} />
            </div>
            <div class="space-y-1">
              <Label for={`mat-gxz-${index}`}>Shear Modulus XZ</Label>
              <Input id={`mat-gxz-${index}`} type="number" bind:value={material.shearModulusXZ} />
            </div>
          {/if}
        </div>
      {/if}

      {#if material.stiffnessMatrix && material.materialSymmetry === 'Anisotropic' && material.matType?.includes('Correspondence')}
        <div class="flex flex-wrap gap-6 border-t border-border pt-3">
          {#if material.stiffnessMatrix.calculateStiffnessMatrix}
            <div class="space-y-2">
              {#each Object.keys(material.stiffnessMatrix.engineeringConstants) as key (key)}
                <div class="space-y-1">
                  <Label for={`mat-ec-${index}-${key}`}>{key}</Label>
                  <Input
                    id={`mat-ec-${index}-${key}`}
                    type="number"
                    bind:value={
                      material.stiffnessMatrix.engineeringConstants[
                        key as keyof typeof material.stiffnessMatrix.engineeringConstants
                      ]
                    }
                    oninput={() => calculateStiffnessMatrix(index)}
                  />
                </div>
              {/each}
            </div>
          {/if}
          <div class="space-y-2">
            {#each Object.keys(material.stiffnessMatrix.matrix) as key (key)}
              <div class="space-y-1">
                <Label for={`mat-mx-${index}-${key}`}>{key}</Label>
                <Input
                  id={`mat-mx-${index}-${key}`}
                  type="number"
                  bind:value={material.stiffnessMatrix.matrix[key as keyof typeof material.stiffnessMatrix.matrix]}
                  readonly={material.stiffnessMatrix.calculateStiffnessMatrix}
                />
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <div class="space-y-1">
        <Label for={`mat-stab-${index}`}>Stabilization Type</Label>
        <select
          id={`mat-stab-${index}`}
          bind:value={material.stabilizationType}
          class="flex h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
        >
          {#each stabilizationTypes as type (type)}
            <option value={type}>{type}</option>
          {/each}
        </select>
      </div>

      {#if material.matType?.some((t) => t.includes('Plastic'))}
        <div class="space-y-1">
          <Label for={`mat-yield-${index}`}>Yield Stress</Label>
          <Input id={`mat-yield-${index}`} type="number" bind:value={material.yieldStress} />
        </div>
      {/if}
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addMaterial}>
    <Plus class="h-4 w-4" /> Add Material
  </Button>

  <input bind:this={multiSoInput} type="file" multiple accept=".so" class="hidden" onchange={onMultiFilePicked} />
  <input bind:this={propsInput} type="file" multiple accept=".inp" class="hidden" onchange={onPropsFilePicked} />
</div>
