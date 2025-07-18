// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

import { defineStore } from 'pinia';

export const useModelStore = defineStore('model', {
  state: () => ({
    modelData: {
      model: {
        modelFolderName: 'Default',
        ownModel: false,
        ownMesh: false,
        length: 0.115,
        cracklength: 0.115,
        notchEnabled: false,
        width: 0.1,
        height: 2.0,
        height2: 1.0,
        radius: 1.0,
        radius2: 1.0,
        discretization: 21,
        horizon: 0.01,
        structured: true,
        twoDimensional: true,
        rotatedAngles: false,
        angles: [0, 0, 0, 0],
        amplitudeFactor: 0.75,
        wavelength: 3.0,
        meshFile: 'Dogbone.txt',
      },
      discretization: {
        discType: 'txt',
        distributionType: 'Neighbor based',
        gcode: {
          overwriteMesh: true,
          sampling: 1,
          width: 0.4,
          scale: 1,
        },
      },
      materials: [
        {
          materialsId: 1,
          name: 'Aluminium',
          matType: ['PD Solid Elastic'],
          materialSymmetry: 'Isotropic',
          bulkModulus: null,
          shearModulus: null,
          youngsModulus: 7.0e5,
          poissonsRatio: 0.33,
          planeStress: true,
          planeStrain: false,
          stabilizationType: 'Global Stiffness',
          thickness: 1.0,
          hourglassCoefficient: 1.0,
          actualHorizon: null,
          yieldStress: null,
          stiffnessMatrix: {
            calculateStiffnessMatrix: false,
            engineeringConstants: {
              E1: null,
              E2: null,
              E3: null,
              G12: null,
              G13: null,
              G23: null,
              nu12: null,
              nu13: null,
              nu23: null,
            },
            matrix: {
              C11: null,
              C12: null,
              C13: null,
              C14: null,
              C15: null,
              C16: null,
              C22: null,
              C23: null,
              C24: null,
              C25: null,
              C26: null,
              C33: null,
              C34: null,
              C35: null,
              C36: null,
              C44: null,
              C45: null,
              C46: null,
              C55: null,
              C56: null,
              C66: null,
            },
          },
          properties: [{ materialsPropId: 1, name: 'Prop_1', value: 0.0 }],
          computePartialStress: false,
          useCollocationNodes: false,
        },
      ],
      thermal: {
        enabled: false,
        thermalModels: [
          {
            thermalModelsId: 1,
            name: 'Thermal Model 1',
            applyThermalFlow: false,
            applyThermalExpansion: false,
            applyHeatTransfer: false,
            thermalType: 'Bond based',
            thermalConductivity: null,
            heatTransferCoefficient: null,
            thermalExpansionCoefficient: null,
            environmentalTemperature: null,
            printTemp: 200.0,
            timeFactor: 1.0,
          },
        ],
      },
      additive: {
        enabled: false,
        additiveModels: [
          {
            additiveModelsId: 1,
            name: 'Additive Model 1',
            additiveType: 'Simple Additive',
            printTemp: 200.0,
            timeFactor: 1,
          },
        ],
      },
      damages: [
        {
          damagesId: 1,
          name: 'Damage',
          damageModel: 'Critical Energy',
          criticalStretch: null,
          criticalEnergy: '1e-8',
          criticalVonMisesStress: null,
          criticalDamage: null,
          thresholdDamage: null,
          criticalDamageToNeglect: null,
          interBlockDamage: false,
          numberOfBlocks: 5,
          interBlocks: [
            {
              damagesInterId: 1,
              firstBlockId: 1,
              secondBlockId: 2,
              value: 0.1,
            },
          ],
          anistropicDamage: false,
          anistropicDamageX: null,
          anistropicDamageY: null,
          anistropicDamageZ: null,
          planeStress: true,
          onlyTension: false,
          detachedNodesCheck: true,
          thickness: 1.0,
          hourglassCoefficient: 1.0,
          stabilizationType: 'Global Stiffness',
          criticalEnergyCalc: {
            calculateCriticalEnergy: false,
            k1c: null,
          },
        },
      ],
      blocks: [
        {
          blocksId: 1,
          name: 'block_1',
          material: 'Aluminium',
          damageModel: '',
          additiveModel: '',
          thermalModel: '',
          horizon: null,
          density: '1.4e-8',
          specificHeatCapacity: null,
          show: true,
        },
        {
          blocksId: 2,
          name: 'block_2',
          material: 'Aluminium',
          damageModel: '',
          additiveModel: '',
          thermalModel: '',
          horizon: null,
          density: '1.4e-8',
          specificHeatCapacity: null,
          show: true,
        },
        {
          blocksId: 3,
          name: 'block_3',
          material: 'Aluminium',
          damageModel: 'Damage',
          additiveModel: '',
          thermalModel: '',
          horizon: null,
          density: '1.4e-8',
          specificHeatCapacity: null,
          show: true,
        },
        {
          blocksId: 4,
          name: 'block_4',
          material: 'Aluminium',
          damageModel: '',
          additiveModel: '',
          thermalModel: '',
          horizon: null,
          density: '1.4e-8',
          specificHeatCapacity: null,
          show: true,
        },
        {
          blocksId: 5,
          name: 'block_5',
          material: 'Aluminium',
          damageModel: '',
          additiveModel: '',
          thermalModel: '',
          horizon: null,
          density: '1.4e-8',
          specificHeatCapacity: null,
          show: true,
        },
      ],
      boundaryConditions: {
        conditions: [
          {
            conditionsId: 1,
            name: 'BC_1',
            nodeSet: 1,
            boundarytype: 'Dirichlet',
            variable: 'Displacements',
            blockId: 1,
            stepId: [1],
            coordinate: 'x',
            value: '0*t',
          },
          {
            conditionsId: 2,
            name: 'BC_2',
            nodeSet: 2,
            boundarytype: 'Dirichlet',
            variable: 'Displacements',
            blockId: 5,
            stepId: [1],
            coordinate: 'x',
            value: '0.5*t',
          },
        ],
        nodeSets: [
          {
            nodeSetId: 1,
            file: 'ns_Dogbone_1.txt',
          },
          {
            nodeSetId: 2,
            file: 'ns_Dogbone_2.txt',
          },
        ],
      },
      bondFilters: [],
      contact: {
        enabled: false,
        contactModels: [
          {
            contactModelId: 1,
            name: 'Contact 1',
            contactType: 'Penalty Contact',
            contactRadius: 0.000775,
            contactStiffness: 1000000000000.0,
            contactGroups: [
              {
                contactGroupId: 1,
                name: 'Contact Group 1',
                masterBlockId: 1,
                slaveBlockId: 2,
                searchRadius: 0.01,
              },
            ],
          },
        ],
      },
      computes: [
        {
          computesId: 1,
          computeClass: 'Block_Data',
          name: 'External_Displacement',
          variable: 'Displacement',
          calculationType: 'Maximum',
          blockName: 'block_5',
          xValue: null,
          yValue: null,
          zValue: null,
        },
        {
          computesId: 2,
          computeClass: 'Block_Data',
          name: 'External_Force',
          variable: 'Force',
          calculationType: 'Sum',
          blockName: 'block_5',
          xValue: null,
          yValue: null,
          zValue: null,
        },
      ],
      preCalculations: {
        deformedBondGeometry: null,
        deformationGradient: null,
        shapeTensor: null,
        bondAssociatedShapeTensor: null,
        bondAssociatedDeformationGradient: null,
      },
      outputs: [
        {
          outputsId: 1,
          name: 'Output1',
          selectedFileType: 'Exodus',
          selectedOutputs: [
            'Displacements',
            'Forces',
            'Damage',
            'von Mises Stress',
          ],
          Write_After_Damage: false,
          Frequency: 100,
          numberOfOutputSteps: 100,
          useOutputFrequency: false,
          InitStep: 0,
        },
        {
          outputsId: 2,
          name: 'Output2',
          selectedFileType: 'CSV',
          selectedOutputs: ['External_Displacement', 'External_Force'],
          Write_After_Damage: false,
          Frequency: 100,
          numberOfOutputSteps: 100,
          useOutputFrequency: false,
          InitStep: 0,
        },
      ],
      solvers: [
        {
          stepId: 1,
          dispEnabled: true,
          matEnabled: true,
          damEnabled: true,
          tempEnabled: false,
          verbose: false,
          calculateCauchy: false,
          calculateVonMises: true,
          calculateStrain: false,
          initialTime: 0.0,
          finalTime: '1e-5',
          solvertype: 'Verlet',
          fixedDt: null,
          safetyFactor: 0.9,
          numericalDamping: 0.0005,
          numberOfLoadSteps: 100,
          verlet: {
            safetyFactor: 0.95,
            numericalDamping: 0.000005,
            outputFrequency: 7500,
          },
          stopAfterDamageInitation: false,
          endStepAfterDamage: 3,
          stopAfterCertainDamage: false,
          maxDamageValue: 0.3,
          stopBeforeDamageInitation: false,
          adaptivetimeStepping: false,
          adapt: {
            stableStepDifference: 4,
            maximumBondDifference: 4,
            stableBondDifference: 1,
          },
        },
      ],
      job: {
        cluster: false,
        sbatch: false,
        verbose: false,
        nodes: 1,
        tasks: 32,
        tasksPerNode: 32,
        cpusPerTask: 1,
        multithread: false,
        time: '00:20:00',
        account: '2263032',
        // mail: 'jan-timo.hesse@dlr.de',
      },
    },
    availableModels: [],
    modelParams: [],
    selectedModel: {
      title: 'Compact Tenison',
      file: 'CompactTension',
    },
  }),
  actions: {
    initialiseStore() {
      if (localStorage.getItem('modelData')) {
        console.log('initialiseStore');
        const object = JSON.parse(localStorage.getItem('modelData'));
        this.modelData = structuredClone(object);
      }
      if (localStorage.getItem('selectedModel')) {
        const object = JSON.parse(localStorage.getItem('selectedModel'));
        this.selectedModel = structuredClone(object);
      }
    },
  },
});
