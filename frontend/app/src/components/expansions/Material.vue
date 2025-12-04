<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="material, index in materials" :key="material.materialsId as PropertyKey" style="padding: 0px">
      <div
        v-bind:style="(material.materialsId! % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
        <h4 class="my-title">Material {{ material.materialsId }}</h4>
        <div class="row my-row">
          <q-input class="my-input" v-model="material.name" :rules="[rules.required, rules.name]"
            :label="materialKeys.name" standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeMaterial(index)">
            <q-tooltip>
              Remove Material
            </q-tooltip>
          </q-btn>
        </div>
        <div class="row my-row">
          <q-select class="my-input" v-model="material.matType" use-input use-chips multiple input-debounce="0"
            :options="filterOptions" @filter="filterFn" style="width: 250px; margin-bottom:20px;"
            :label="materialKeys.matType" standout dense></q-select>
        </div>
        <div v-if="material.matType.includes('User')">
          <q-list v-for="prop, subindex in material.properties" :key="prop.materialsPropId as PropertyKey"
            style="padding: 0px">
            <div class="row my-row">
              <q-input class="my-input" v-model="prop.value" :rules="[rules.required, rules.float]" :label="prop.name"
                standout dense></q-input>
              <q-btn flat icon="fas fa-trash-alt" @click="removeProp(index, subindex)">
                <q-tooltip>
                  Remove Property
                </q-tooltip>
              </q-btn>
            </div>
          </q-list>
          <div class="row my-row">
            <q-btn flat icon="fas fa-plus" @click="addProp(index)">
              <q-tooltip>
                Add Property
              </q-tooltip>
            </q-btn>
          </div>
          <div class="row my-row">
            <q-btn flat icon="fas fa-upload" @click="uploadProps(index)">
              <q-tooltip>
                Upload Property
              </q-tooltip>
            </q-btn>

            <q-btn flat icon="fas fa-upload" @click="uploadSo">
              <q-tooltip>
                Upload shared Librarie
              </q-tooltip>
            </q-btn>
            <q-input class="my-input" v-model="material.numStateVars" :rules="[rules.required, rules.int]"
              :label="materialKeys.numStateVars" @update:model-value="editNumStateVars(material.numStateVars!)" standout
              dense></q-input>
          </div>
        </div>
        <div class="row my-row">
          <q-input class="my-input" v-model="material.poissonsRatio" :rules="[rules.required, rules.float]"
            :label="materialKeys.poissonsRatio" clearable standout dense></q-input>
        </div>
        <div class="row my-row">
          <q-input class="my-input" v-model="material.bulkModulus" :rules="[rules.required, rules.float]"
            :label="materialKeys.bulkModulus" clearable standout dense></q-input>
          <q-input class="my-input" v-model="material.shearModulus" :rules="[rules.required, rules.float]"
            :label="materialKeys.shearModulus" clearable standout dense></q-input>
          <q-input class="my-input" v-model="material.youngsModulus" :rules="[rules.required, rules.float]"
            :label="materialKeys.youngsModulus" clearable standout dense></q-input>
        </div>
        <div class="row my-row">
          <q-select class="my-input" :options="materialSymmetry" v-model="material.materialSymmetry"
            :label="materialKeys.materialSymmetry" standout dense></q-select>
          <q-toggle class="my-toggle" v-model="material.planeStress" :label="materialKeys.planeStress" standout
            dense></q-toggle>
          <q-toggle class="my-toggle" v-model="material.planeStrain" :label="materialKeys.planeStrain" standout
            dense></q-toggle>
          <q-toggle
            v-if="material.stiffnessMatrix && material.materialSymmetry == 'Anisotropic' && material.matType.includes('Correspondence')"
            class="my-toggle" v-model="material.stiffnessMatrix.calculateStiffnessMatrix"
            :label="materialKeys.stiffnessMatrix.calculateStiffnessMatrix" standout dense></q-toggle>
        </div>
        <div class="row my-row"
          v-if="material.stiffnessMatrix && material.materialSymmetry == 'Anisotropic' && material.matType.includes('Correspondence')">
          <q-list v-if="material.stiffnessMatrix.calculateStiffnessMatrix" style="padding: 0px">
            <q-item v-for="(value, key) in material.stiffnessMatrix.engineeringConstants" :key="key">
              <q-input class="my-input" v-model="material.stiffnessMatrix.engineeringConstants[key]"
                :rules="[rules.required, rules.float]" :label="materialKeys.stiffnessMatrix.engineeringConstants[key]"
                standout dense @update:model-value="calculateStiffnessMatrix(index)" clearable></q-input>
            </q-item>
          </q-list>
          <q-list style="padding: 0px">
            <q-item v-for="(value, key) in material.stiffnessMatrix.matrix" :key="key">
              <q-input class="my-input" v-model="material.stiffnessMatrix.matrix[key]"
                :rules="[rules.required, rules.float]" :label="materialKeys.stiffnessMatrix.matrix[key]" standout dense
                :readonly="material.stiffnessMatrix.calculateStiffnessMatrix!"></q-input>
            </q-item>
          </q-list>
        </div>
        <div class="row my-row">
          <q-select class="my-input" :options="stabilizationType" v-model="material.stabilizationType"
            :label="materialKeys.stabilizationType" standout dense></q-select>
        </div>
        <!-- <div class="row my-row">
          <q-input class="my-input" v-model="material.thickness" :rules="[rules.required, rules.float]"
            :label="materialKeys.thickness" standout dense></q-input>
        </div> -->
        <!-- <div class="row my-row">
          <q-input class="my-input" v-model="material.hourglassCoefficient" :rules="[rules.required, rules.float]"
            :label="materialKeys.hourglassCoefficient" standout dense></q-input>
        </div> -->
        <!-- <div class="row my-row" v-show="material.matType == 'Elastic Plastic Hypoelastic Correspondence'">
          <q-input class="my-input" v-model="material.actualHorizon" :rules="[rules.required, rules.float]"
            :label="materialKeys.actualHorizon" standout dense></q-input>
        </div> -->
        <div class="row my-row" v-show="material.matType.some(type => type.includes('Plastic'))">
          <q-input class="my-input" v-model="material.yieldStress" :rules="[rules.required, rules.float]"
            :label="materialKeys.yieldStress" standout dense></q-input>
        </div>
      </div>
    </q-list>
    <q-btn flat icon="fas fa-plus" @click="addMaterial">
      <q-tooltip>
        Add Material
      </q-tooltip>
    </q-btn>
    <input type="file" style="display: none" ref="multiSoInput" multiple accept=".so" @change="onMultiFilePicked" />
    <input type="file" style="display: none" ref="propsInput" multiple accept=".inp" @change="onPropsFilePicked" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { useViewStore } from 'src/stores/view-store';
import rules from 'assets/rules.js';
import { matrix, inv } from 'mathjs'
import { uploadFiles } from 'src/client';
import type { Material, properties } from 'src/client';

export default defineComponent({
  name: 'MaterialSettings',
  setup() {
    const store = useModelStore();
    const viewStore = useViewStore();
    const materials = computed(() => store.modelData.materials) as unknown as Material[]
    const job = computed(() => store.modelData.job)
    const modelData = computed(() => store.modelData)
    return {
      store,
      viewStore,
      materials,
      job,
      modelData,
      rules
    }
  },
  created() {
  },
  data() {
    return {
      selectedMaterial: 0,
      // materialModelName: [
      //     'Diffusion',
      //     'Elastic',
      //     'Elastic Bond Based',
      //     'Elastic Bond Associated Correspondence',
      //     'Anisotropic Elastic Bond Associated Correspondence',
      //     'Elastic Correspondence',
      //     'Elastic Correspondence Partial Stress',
      //     'Elastic Hypoelastic Correspondence',
      //     'Elastic Partial Volume',
      //     'Elastic Plastic',
      //     'Elastic Plastic Correspondence',
      //     'Elastic Plastic Hardening',
      //     'Elastic Plastic Hypoelastic Correspondence',
      //     'Isotropic Hardening Correspondence',
      //     'Isotropic Hardening Hypoelastic Correspondence',
      //     'LCM',
      //     'Linear Elastic Correspondence',
      //     'Linear LPS Partial Volume',
      //     'Multiphysics Elastic',
      //     'Pals',
      //     'Pressure Dependent Elastic Plastic',
      //     'User Correspondence',
      //     'Viscoelastic',
      //     'Viscoplastic Needleman Correspondence',
      //     'Vector Poisson',
      //     'PD Solid Elastic',
      // ],
      materialModelNames: [
        'Bond-based Elastic',
        'PD Solid Elastic',
        'PD Solid Plastic',
        'Correspondence Elastic',
        'Correspondence Plastic'
      ],
      materialSymmetry: ['Isotropic', 'Anisotropic'],
      stabilizationType: [
        'Bond Based',
        'State Based',
        'Sub Horizon',
        'Global Stiffness',
      ],
      micofam: {
        RVE: {
          rve_fvc: 30,
          rve_radius: 6.6,
          rve_lgth: 50,
          rve_dpth: 1,
        },
        Mesh: {
          mesh_fib: 35,
          mesh_lgth: 35,
          mesh_dpth: 1,
          mesh_aa: 'on',
        },
      },
      materialKeys: {
        name: 'name',
        matType: 'Material Models',
        materialSymmetry: 'Material Symmetry',
        bulkModulus: 'Bulk Modulus',
        shearModulus: 'Shear Modulus',
        youngsModulus: "Young's Modulus",
        poissonsRatio: "Poisson's Ratio",
        planeStress: 'Plane Stress',
        planeStrain: 'Plane Strain',
        stabilizationType: 'Stabilization Type',
        thickness: 'Thickness',
        hourglassCoefficient: 'Hourglass Coefficient',
        actualHorizon: 'Actual Horizon',
        yieldStress: 'Yield Stress',
        stiffnessMatrix: {
          calculateStiffnessMatrix: 'Calculate Stiffness Matrix',
          engineeringConstants: {
            E1: 'E1',
            E2: 'E2',
            E3: 'E3',
            G12: 'G12',
            G13: 'G13',
            G23: 'G23',
            nu12: 'nu12',
            nu13: 'nu13',
            nu23: 'nu23'
          },
          matrix: {
            C11: 'C11',
            C12: 'C12',
            C13: 'C13',
            C14: 'C14',
            C15: 'C15',
            C16: 'C16',
            C22: 'C22',
            C23: 'C23',
            C24: 'C24',
            C25: 'C25',
            C26: 'C26',
            C33: 'C33',
            C34: 'C34',
            C35: 'C35',
            C36: 'C36',
            C44: 'C44',
            C45: 'C45',
            C46: 'C46',
            C55: 'C55',
            C56: 'C56',
            C66: 'C66'
          }
        },
        computePartialStress: 'Compute Partial Stress',
        useCollocationNodes: 'Use Collocation Nodes',
        numStateVars: 'Number of State Vars',
      },
      filterOptions: [] as string[],
    };
  },
  methods: {
    editNumStateVars(numStateVars: number) {
      this.$bus.emit('addStateVarsToOutput', numStateVars)
    },
    filterFn(val: string, update: (callbackFn: () => void) => void) {
      update(() => {
        if (val === '') {
          this.filterOptions = this.materialModelNames
        }
        else {
          const needle = val.toLowerCase()
          this.filterOptions = this.materialModelNames.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    },
    calculateStiffnessMatrix(materialId: number) {
      if (this.materials[materialId]!.stiffnessMatrix && this.materials[materialId]!.stiffnessMatrix.calculateStiffnessMatrix) {

        const E1 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.E1 as number | null;   // Elastic modulus along the fiber direction (Pa)
        const E2 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.E2 as number | null;    // Elastic modulus transverse to the fiber direction (Pa)
        let E3 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.E3 as number | null;    // Elastic modulus transverse to the fiber direction (Pa)
        const G12 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.G12 as number | null;    // Shear modulus in the 1-2 plane (Pa)
        let G13 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.G13 as number | null;    // Shear modulus in the 1-3 plane (Pa)
        let G23 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.G23 as number | null;    // Shear modulus in the 2-3 plane (Pa)
        const nu12 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.nu12 as number | null;   // Poisson's ratio in the 1-2 plane
        let nu13 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.nu13 as number | null;   // Poisson's ratio in the 1-3 plane
        let nu23 = this.materials[materialId]!.stiffnessMatrix.engineeringConstants.nu23 as number | null;   // Poisson's ratio in the 2-3 plane

        if (E1 != null && E2 != null && G12 != null && nu12 != null) {

          if (E3 === null) E3 = E2;
          if (G13 === null) G13 = G12;
          if (nu13 === null) nu13 = nu12;
          if (nu23 === null) nu23 = nu12;
          if (G23 === null) G23 = E2 / (2 * (1 + nu23));

          const compliance = matrix([
            [1 / E1, -nu12 / E1, -nu13 / E1, 0, 0, 0],
            [-nu12 / E1, 1 / E2, -nu23 / E2, 0, 0, 0],
            [-nu13 / E1, -nu23 / E2, 1 / E3, 0, 0, 0],
            [0, 0, 0, 1 / G23, 0, 0],
            [0, 0, 0, 0, 1 / G13, 0],
            [0, 0, 0, 0, 0, 1 / G12]
          ]);
          const stiffness = inv(compliance);
          const stiffnessArray = stiffness.toArray() as number[][];

          this.materials[materialId]!.stiffnessMatrix.matrix = {
            C11: Number(stiffnessArray[0]![0]),
            C12: Number(stiffnessArray[0]![1]),
            C13: Number(stiffnessArray[0]![2]),
            C14: Number(stiffnessArray[0]![3]),
            C15: Number(stiffnessArray[0]![4]),
            C16: Number(stiffnessArray[0]![5]),
            C22: Number(stiffnessArray[1]![1]),
            C23: Number(stiffnessArray[1]![2]),
            C24: Number(stiffnessArray[1]![3]),
            C25: Number(stiffnessArray[1]![4]),
            C26: Number(stiffnessArray[1]![5]),
            C33: Number(stiffnessArray[2]![2]),
            C34: Number(stiffnessArray[2]![3]),
            C35: Number(stiffnessArray[2]![4]),
            C36: Number(stiffnessArray[2]![5]),
            C44: Number(stiffnessArray[3]![3]),
            C45: Number(stiffnessArray[3]![4]),
            C46: Number(stiffnessArray[3]![5]),
            C55: Number(stiffnessArray[4]![4]),
            C56: Number(stiffnessArray[4]![5]),
            C66: Number(stiffnessArray[5]![5]),
          };
        }
      }
    },
    // @ts-expect-error Bla
    onMultiFilePicked(event) {
      const files = event.target.files;
      // const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.viewStore.modelLoading = true;
      this.uploadfiles(files);

      this.viewStore.modelLoading = false;
    },
    // @ts-expect-error Bla
    uploadfiles(files) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
      // @ts-expect-error Bla
      uploadFiles({ modelName: this.store.selectedModel.title, modelFolderName: this.modelData.model.modelFolderName, formData: formData })
        .then(() => {
          this.$q.notify({
            message: 'File uploaded'
          })
        })
        .catch((error) => {
          this.$q.notify({
            type: 'negative',
            message: error.response.detail
          })
        })
    },
    uploadSo() {
      // @ts-expect-error Bla
      this.$refs.multiSoInput.click();
    },
    uploadProps(id: number) {
      // @ts-expect-error Bla
      this.$refs.propsInput.click();
      this.selectedMaterial = id;
    },
    onPropsFilePicked(event: Event) {
      if (!event.target) {
        return;
      }
      // @ts-expect-error Bla
      const files = event.target.files;

      const fr = new FileReader();
      fr.onload = (e) => {
        const input_string = e.target!.result as string;

        const filtered_string = input_string.match(/\*User([\D\S]*?)\*/gi) as string[];
        console.log(filtered_string)
        let propsArray = filtered_string[0]!.split(/[\n,]/gi);
        console.log(propsArray)
        propsArray = propsArray.filter(value => value.trim() !== ''); // Remove empty values
        console.log(propsArray);
        propsArray = propsArray.slice(0, propsArray.length - 1);
        console.log(propsArray)

        const numConstants = propsArray.length - 2; // Determine number of constants dynamically
        console.log(numConstants)
        // console.log(propsArray[1].match(/\d+/))
        if (!propsArray[1]) {
          console.log('Constants not found.');
          return;
        }
        const numConstantsFound = propsArray[1].match(/\d+/);
        if (!numConstantsFound) {
          console.log('Number of constants not found.');
          return;
        }
        if (parseFloat(numConstantsFound[0]) == numConstants) {
          this.materials[0]!.properties = [];

          // Extract parameter values
          const parameterString = input_string.match(/\*PARAMETER([\D\S]*?)\*HEADING/gi);
          if (!parameterString) {
            console.log('Parameter string not found.');
            return;
          }
          const parameterValues = parameterString[0].match(/\w+=([\d.]+)/gi);
          if (!parameterValues) {
            console.log('Parameter values not found.');
            return;
          }
          console.log(parameterValues);

          for (let i = 2; i < propsArray.length; i++) {
            this.addProp(0);

            // Replace placeholders with parameter values
            let propValue = propsArray[i]!.trim();
            if (propValue.startsWith('<') && propValue.endsWith('>')) {
              const paramName = propValue.slice(1, -1);
              const paramValue = parameterValues.find(param => param.startsWith(paramName + '='));
              if (paramValue) {
                propValue = paramValue.split('=')[1]!;
              } else {
                console.log(`Parameter ${paramName} not found.`);
              }
            }

            this.materials[0]!.properties[i - 2]!.value = parseFloat(propValue);
          }
        } else {
          console.log('Length of Propsarray unexpected');
        }
      };
      fr.readAsText(files.item(0));

      // console.log(input_string)
      // let filtered_string = input_string.search(/\*User([\D\S]*?)\*/i);
    },
    addMaterial() {
      if (!this.materials) {
        this.materials = []
      }
      const len = this.materials.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.materials[len - 1])) as Material : {} as Material;
      newItem.materialsId = 1
      newItem.name = 'Material 1'
      this.materials.push(newItem);
    },
    removeMaterial(index: number) {
      this.materials.splice(index, 1);
      this.materials.forEach((model, i) => {
        model.materialsId = i + 1
      })
    },
    addProp(index: number) {
      const len = this.materials[index]!.properties!.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.materials[len - 1])) as properties : {} as properties;
      newItem.materialsPropId = len + 1
      newItem.name = 'Prop_' + (len + 1)

      this.materials[index]!.properties!.push(newItem)
    },
    removeProp(index: number, subindex: number) {
      this.materials[index]!.properties!.splice(subindex, 1);
    },
  }
})
</script>
