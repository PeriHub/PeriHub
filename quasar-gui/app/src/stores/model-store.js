import { defineStore } from "pinia";
import { parseFromJson } from '../utils/functions.js'

export const useModelStore = defineStore("model", {
  state: () => ({
    modelData: {
      model: {
        modelNameSelected: "Dogbone",
        ownModel: false,
        ownMesh: false,
        translated: false,
        length: 0.115,
        cracklength: 0.115,
        notchEnabled: false,
        width: 0.003,
        height: 0.019,
        height2: 0.013,
        radius: 1.0,
        discretization: 21,
        horizon: 0.01,
        structured: true,
        twoDimensional: true,
        rotatedAngles: false,
        angles: [0, 0, 0, 0],
        amplitudeFactor: 0.75,
        wavelength: 3.0,
        meshFile: "Dogbone.txt",
      },
      materials: [
        {
          materialsId: 1,
          name: "PMMA",
          matType: "Linear Elastic Correspondence",
          density: 1.4e5,
          bulkModulus: null,
          shearModulus: null,
          youngsModulus: 2.997e9,
          poissonsRatio: 0.3,
          tensionSeparation: false,
          nonLinear: true,
          planeStress: true,
          materialSymmetry: "Isotropic",
          stabilizatonType: "Global Stiffness",
          thickness: 0.01,
          hourglassCoefficient: 1.0,
          actualHorizon: null,
          yieldStress: null,
          Parameter: [
            { name: "C11", value: 0.0 },
            { name: "C12", value: 0.0 },
            { name: "C13", value: 0.0 },
            { name: "C14", value: 0.0 },
            { name: "C15", value: 0.0 },
            { name: "C16", value: 0.0 },
            { name: "C22", value: 0.0 },
            { name: "C23", value: 0.0 },
            { name: "C24", value: 0.0 },
            { name: "C25", value: 0.0 },
            { name: "C26", value: 0.0 },
            { name: "C33", value: 0.0 },
            { name: "C34", value: 0.0 },
            { name: "C35", value: 0.0 },
            { name: "C36", value: 0.0 },
            { name: "C44", value: 0.0 },
            { name: "C45", value: 0.0 },
            { name: "C46", value: 0.0 },
            { name: "C55", value: 0.0 },
            { name: "C56", value: 0.0 },
            { name: "C66", value: 0.0 },
          ],
          properties: [{ materialsPropId: 1, name: "Prop_1", value: 0.0 }],
          computePartialStress: false,
          useCollocationNodes: false,
          // Thermal
          specificHeatCapacity: null,
          thermalConductivity: null,
          heatTransferCoefficient: null,
          applyThermalFlow: false,
          applyThermalStrain: false,
          applyHeatTransfer: false,
          thermalExpansionCoefficient: null,
          environmentalTemperature: null,
          // 3dPrint
          volumeFactor: null,
          volumeLimit: null,
          surfaceCorrection: null,
        },
        {
          materialsId: 2,
          name: "PMMAElast",
          matType: "Linear Elastic Correspondence",
          density: 1.4e5,
          bulkModulus: null,
          shearModulus: null,
          youngsModulus: 2.997e9,
          poissonsRatio: 0.3,
          tensionSeparation: false,
          nonLinear: true,
          planeStress: true,
          materialSymmetry: "Isotropic",
          stabilizatonType: "Global Stiffness",
          thickness: 0.01,
          hourglassCoefficient: 1.0,
          actualHorizon: null,
          yieldStress: null,
          Parameter: [
            { name: "C11", value: 165863.6296530634 },
            { name: "C12", value: 4090.899504376252 },
            { name: "C13", value: 2471.126276093059 },
            { name: "C14", value: 0.0 },
            { name: "C15", value: 0.0 },
            { name: "C16", value: 0.0 },
            { name: "C22", value: 9217.158022124806 },
            { name: "C23", value: 2471.126276093059 },
            { name: "C24", value: 0.0 },
            { name: "C25", value: 0.0 },
            { name: "C26", value: 0.0 },
            { name: "C33", value: 9217.158022124804 },
            { name: "C34", value: 0.0 },
            { name: "C35", value: 0.0 },
            { name: "C36", value: 0.0 },
            { name: "C44", value: 3360.0 },
            { name: "C45", value: 0.0 },
            { name: "C46", value: 0.0 },
            { name: "C55", value: 4200.0 },
            { name: "C56", value: 0.0 },
            { name: "C66", value: 4200.0 },
          ],
          properties: [{ materialsPropId: 1, name: "Prop_1", value: 0.0 }],
          computePartialStress: false,
          useCollocationNodes: false,
          // Thermal
          specificHeatCapacity: null,
          thermalConductivity: null,
          heatTransferCoefficient: null,
          applyThermalFlow: false,
          applyThermalStrain: false,
          applyHeatTransfer: false,
          thermalExpansionCoefficient: null,
          environmentalTemperature: null,
          // 3dPrint
          volumeFactor: null,
          volumeLimit: null,
          surfaceCorrection: null,
        },
      ],
      damages: [
        {
          damagesId: 1,
          name: "PMMADamage",
          damageModel: "Critical Energy Correspondence",
          criticalStretch: 10,
          criticalEnergy: 10.1,
          criticalVonMisesStress: 10.0,
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
          planeStress: true,
          onlyTension: false,
          detachedNodesCheck: true,
          thickness: 10.0,
          hourglassCoefficient: 1.0,
          stabilizatonType: "Global Stiffness",
          criticalEnergyCalc: {
            calculateCriticalEnergy: false,
            k1c: null,
          },
        },
      ],
      blocks: [
        {
          blocksId: 1,
          name: "block_1",
          material: "PMMAElast",
          damageModel: "",
          horizon: null,
          show: true,
        },
        {
          blocksId: 2,
          name: "block_2",
          material: "PMMAElast",
          damageModel: "",
          horizon: null,
          show: true,
        },
        {
          blocksId: 3,
          name: "block_3",
          material: "PMMA",
          damageModel: "PMMADamage",
          horizon: null,
          show: true,
        },
        {
          blocksId: 4,
          name: "block_4",
          material: "PMMAElast",
          damageModel: "",
          horizon: null,
          show: true,
        },
        {
          blocksId: 5,
          name: "block_5",
          material: "PMMAElast",
          damageModel: "",
          horizon: null,
          show: true,
        },
      ],
      boundaryConditions: {
        conditions: [
          {
            conditionsId: 1,
            name: "BC_1",
            nodeSet: 1,
            boundarytype: "Prescribed Displacement",
            blockId: 1,
            coordinate: "x",
            value: "0*t",
          },
          {
            conditionsId: 2,
            name: "BC_2",
            nodeSet: 2,
            boundarytype: "Prescribed Displacement",
            blockId: 5,
            coordinate: "x",
            value: "0.05*t",
          },
        ],
        nodeSets: [
          {
            nodeSetId: 1,
            file: "ns_Dogbone_1.txt",
          },
          {
            nodeSetId: 2,
            file: "ns_Dogbone_2.txt",
          },
        ],
      },
      bondFilters: [
        {
          bondFiltersId: 1,
          name: "bf_1",
          type: "Rectangular_Plane",
          normalX: 0.0,
          normalY: 1.0,
          normalZ: 0.0,
          lowerLeftCornerX: -0.5,
          lowerLeftCornerY: 25.0,
          lowerLeftCornerZ: -0.5,
          bottomUnitVectorX: 1.0,
          bottomUnitVectorY: 0.0,
          bottomUnitVectorZ: 0.0,
          bottomLength: 50.5,
          sideLength: 1.0,
          centerX: 0.0,
          centerY: 1.0,
          centerZ: 0.0,
          radius: 1.0,
          show: true,
        },
        {
          bondFiltersId: 2,
          name: "bf_2",
          type: "Rectangular_Plane",
          normalX: 0.0,
          normalY: 1.0,
          normalZ: 0.0,
          lowerLeftCornerX: -0.5,
          lowerLeftCornerY: -25.0,
          lowerLeftCornerZ: -0.5,
          bottomUnitVectorX: 1.0,
          bottomUnitVectorY: 0.0,
          bottomUnitVectorZ: 0.0,
          bottomLength: 50.5,
          sideLength: 1.0,
          centerX: 0.0,
          centerY: 1.0,
          centerZ: 0.0,
          radius: 1.0,
          show: true,
        },
      ],
      contact: {
        enabled: true,
        searchRadius: 0.01,
        searchFrequency: 100,
        contactModels: [
          {
            contactModelsId: 1,
            name: "Contact Model",
            contactType: "Short Range Force",
            contactRadius: 0.000775,
            springConstant: 1000000000000.0,
          },
        ],
        interactions: [
          {
            contactInteractionsId: 1,
            firstBlockId: 1,
            secondBlockId: 2,
            contactModelId: 1,
          },
        ],
      },
      computes: [
        {
          computesId: 1,
          computeClass: "Block_Data",
          name: "External_Displacement",
          variable: "Displacement",
          calculationType: "Maximum",
          blockName: "block_5",
          xValue: null,
          yValue: null,
          zValue: null,
        },
        {
          computesId: 2,
          computeClass: "Block_Data",
          name: "External_Force",
          variable: "Force",
          calculationType: "Sum",
          blockName: "block_5",
          xValue: null,
          yValue: null,
          zValue: null,
        },
      ],
      outputs: [
        {
          outputsId: 1,
          name: "Output1",
          selectedOutputs: [],

          Write_After_Damage: false,
          Frequency: 100,
          InitStep: 0,
        },
      ],
      solver: {
        verbose: false,
        initialTime: 0.0,
        finalTime: 0.0075,
        solvertype: "Verlet",
        fixedDt: null,
        safetyFactor: 0.9,
        numericalDamping: 0.0005,
        peridgimPreconditioner: "None",
        nonlinearSolver: "Line Search Based",
        numberOfLoadSteps: 100,
        maxSolverIterations: 50,
        relativeTolerance: 0.00000001,
        maxAgeOfPrec: 100,
        directionMethod: "Newton",
        newton: { jacobianOperator: "Matrix-Free", preconditioner: "None" },
        lineSearchMethod: "Polynomial",
        verletSwitch: true,
        verlet: {
          safetyFactor: 0.95,
          numericalDamping: 0.000005,
          outputFrequency: 7500,
        },
        stopAfterDamageInitation: false,
        endStepAfterDamage: 3,
        stopBeforeDamageInitation: false,
        adaptivetimeStepping: false,
        adapt: {
          stableStepDifference: 4,
          maximumBondDifference: 4,
          stableBondDifference: 1,
        },
        filetype: "yaml",
      },
      job: {
        cluster: "None",
        tasks: 1,
        time: "00:20:00",
        // user: 'hess_ja',
        account: "2263032",
        // mail: 'jan-timo.hesse@dlr.de',
      },
    },
  }),
  actions: {
    initialiseStore() {
      if (localStorage.getItem("modelData")){
        var object = JSON.parse(localStorage.getItem("modelData"))
        parseFromJson(this.modelData,object)
      }
    },
  },
});