import axios from "axios";
import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere

// import highlighting library (you can use any library you want just return html string)
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles

import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import GIICmodelImage from "../assets/models/GIICmodel/GIICmodel.jpg";
import GIICmodelFile from "../assets/models/GIICmodel/GIICmodel.json";
import GICmodelImage from "../assets/models/GICmodel/GICmodel.jpg";
import GICmodelFile from "../assets/models/GICmodel/GICmodel.json";
import DCBmodelImage from "../assets/models/DCBmodel/DCBmodel.jpg";
import DCBmodelFile from "../assets/models/DCBmodel/DCBmodel.json";
import DogboneImage from "../assets/models/Dogbone/Dogbone.jpg";
import DogboneFile from "../assets/models/Dogbone/Dogbone.json";
import KalthoffWinklerImage from "../assets/models/Kalthoff-Winkler/Kalthoff-Winkler.jpg";
import KalthoffWinklerFile from "../assets/models/Kalthoff-Winkler/Kalthoff-Winkler.json";
import PlateWithHoleImage from "../assets/models/PlateWithHole/PlateWithHole.jpg";
import PlateWithHoleFile from "../assets/models/PlateWithHole/PlateWithHole.json";
import CompactTensionImage from "../assets/models/CompactTension/CompactTension.jpg";
import CompactTensionFile from "../assets/models/CompactTension/CompactTension.json";
import SmetanaImage from "../assets/models/Smetana/Smetana.jpg";
import SmetanaFile from "../assets/models/Smetana/Smetana.json";
import { Plotly } from "vue-plotly";
// import { faLessThanEqual } from '@fortawesome/free-solid-svg-icons';
import Driver from "driver.js";
import "driver.js/dist/driver.min.css";

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

export default {
  name: "PeriHub",
  components: {
    PrismEditor,
    Splitpanes,
    Pane,
    Plotly,
    // pdf
    // RemoteComponent
  },
  data() {
    return {
      // Model
      modelName: [
        "Dogbone",
        "Kalthoff-Winkler",
        "PlateWithHole",
        "GICmodel",
        "GIICmodel",
        "DCBmodel",
        "CompactTension",
        "Smetana",
      ], //, 'RVE'],
      model: {
        modelNameSelected: "Dogbone",
        ownModel: false,
        ownMesh: false,
        translated: false,
        length: 0.115,
        cracklength: 0.115,
        width: 0.003,
        height: 0.019,
        height2: 0.013,
        radius: 1.0,
        discretization: 21,
        horizon: 0.01,
        structured: true,
        twoDimensional: true,
        rotatedAngles: false,
        angles: [0, 0],
        amplitudeFactor: 0.75,
        wavelength: 3.0,
      },
      // Material
      materialModelName: [
        "Diffusion",
        "Elastic",
        "Elastic Bond Based",
        "Elastic Correspondence",
        "Elastic Correspondence Partial Stress",
        "Elastic Hypoelastic Correspondence",
        "Elastic Partial Volume",
        "Elastic Plastic",
        "Elastic Plastic Correspondence",
        "Elastic Plastic Hardening",
        "Elastic Plastic Hypoelastic Correspondence",
        "Isotropic Hardening Correspondence",
        "Isotropic Hardening Hypoelastic Correspondence",
        "LCM",
        "Linear Elastic Correspondence",
        "Linear LPS Partial Volume",
        "Multiphysics Elastic",
        "Pals",
        "Pressure Dependent Elastic Plastic",
        "User Correspondence",
        "Viscoelastic",
        "Viscoplastic Needleman Correspondence",
        "Vector Poisson",
      ],
      materialSymmetry: ["Isotropic", "Anisotropic"],
      stabilizatonType: [
        "Bond Based",
        "State Based",
        "Sub Horizon",
        "Global Stiffness",
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
          mesh_aa: "on",
        },
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
        },
      ],
      materialKeys: {
        name: "name",
        matType: "Material Model",
        density: "Density",
        bulkModulus: "Bulk Modulus",
        shearModulus: "Shear Modulus",
        youngsModulus: "Young's Modulus",
        poissonsRatio: "Poisson's Ratio",
        tensionSeparation: "Tension Separation",
        nonLinear: "Non linear",
        planeStress: "Plane Stress",
        materialSymmetry: "Material Symmetry",
        stabilizatonType: "Stabilizaton Type",
        thickness: "Thickness",
        hourglassCoefficient: "Hourglass Coefficient",
        actualHorizon: "Actual Horizon",
        yieldStress: "Yield Stress",
      },
      // Damage
      damageModelName: [
        "Critical Stretch",
        "Interface Aware",
        "Time Dependent Critical Stretch",
        "Critical Energy",
        "Initial Damage",
        "Time Dependent Critical Stretch",
        "Critical Energy Correspondence",
      ],
      damages: [
        {
          damagesId: 1,
          name: "PMMADamage",
          damageModel: "Critical Energy Correspondence",
          criticalStretch: 10,
          criticalEnergy: 10.1,
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
        },
      ],
      damageKeys: {
        name: "name",
        damageModel: "Damage Model",
        criticalStretch: "Critical Stretch",
        criticalEnergy: "Critical Energy",
        interBlockDamage: "Interblock Damage",
        numberOfBlocks: "Number of Blocks",
        interBlockCriticalEnergy: "Interblock Critical Energy",
        planeStress: "Plane Stress",
        onlyTension: "Only Tension",
        detachedNodesCheck: "Detached Nodes Check",
        thickness: "Thickness",
        hourglassCoefficient: "Hourglass Coefficient",
        stabilizatonType: "Stabilizaton Type",
      },
      // Blocks
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
      blockKeys: {
        name: "name",
        material: "Material",
        damageModel: "Damage Model",
      },
      //  boundaryConditions
      boundarytype: [
        "Initial Displacement",
        "Initial Velocity",
        "Prescribed Displacement",
        "Prescribed Fluid Pressure U",
        "Initial Fluid Pressure U",
        "Initial Temperature",
        "Prescribed Temperature",
        "Thermal Flux",
        "Body Force",
      ],
      coordinate: ["x", "y", "z"],
      boundaryConditions: [
        {
          boundaryConditionsId: 1,
          name: "BC_1",
          nodeSet: null,
          boundarytype: "Prescribed Displacement",
          blockId: 1,
          coordinate: "x",
          value: "0*t",
        },
        {
          boundaryConditionsId: 2,
          name: "BC_2",
          nodeSet: null,
          boundarytype: "Prescribed Displacement",
          blockId: 5,
          coordinate: "x",
          value: "0.05*t",
        },
      ],
      boundaryKeys: {
        name: "name",
        nodeSet: "Node Set",
        boundarytype: "Type",
        blockId: 1,
        coordinate: "Coordinate",
        value: "Value",
      },
      //  bondFilters
      boundarytype: [
        "Initial Displacement",
        "Initial Velocity",
        "Prescribed Displacement",
        "Prescribed Fluid Pressure U",
        "Initial Fluid Pressure U",
        "Initial Temperature",
        "Prescribed Temperature",
        "Thermal Flux",
        "Body Force",
      ],
      bondFiltertype: ["Rectangular_Plane", "Disk"],
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
      bondFilterKeys: {
        name: "name",
        type: "Type",
        normalX: "Normal_X",
        normalY: "Normal_Y",
        normalZ: "Normal_Z",
        lowerLeftCornerX: "Lower_Left_Corner_X",
        lowerLeftCornerY: "Lower_Left_Corner_Y",
        lowerLeftCornerZ: "Lower_Left_Corner_Z",
        bottomUnitVectorX: "Bottom_Unit_Vector_X",
        bottomUnitVectorY: "Bottom_Unit_Vector_Y",
        bottomUnitVectorZ: "Bottom_Unit_Vector_Z",
        bottomLength: "Bottom_Length",
        sideLength: "Side_Length",
        centerX: "Center_X",
        centerY: "Center_Y",
        centerZ: "Center_Z",
        radius: "Radius",
      },
      //  contact
      contactType: ["Short Range Force"],
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
      // Compute
      calculationType: ["Sum", "Maximum", "Minimum"],
      variables: ["Force", "Displacement", "Damage"],
      computes: [
        {
          computesId: 1,
          name: "External_Displacement",
          variable: "Displacement",
          calculationType: "Maximum",
          blockName: "block_5",
        },
        {
          computesId: 2,
          name: "External_Force",
          variable: "Force",
          calculationType: "Sum",
          blockName: "block_5",
        },
      ],
      computeKeys: {
        name: "Output Label",
        variable: "Variable",
        calculationType: "Calculation Type",
        blockName: "Block",
      },
      // Output
      outputs: [
        {
          outputsId: 1,
          name: "Output1",
          Displacement: true,
          Force: true,
          Damage: true,
          Velocity: false,
          Partial_Stress: true,
          Number_Of_Neighbors: false,
          Contact_Force: false,
          Horizon: false,
          Model_Coordinates: false,
          Local_Angles: false,
          Coordinates: false,
          Acceleration: false,
          Temperature: false,
          Temperature_Change: false,
          Force_Density: false,
          External_Force_Density: false,
          Damage_Model_Data: false,
          Velocity_Gradient: false,
          PiolaStressTimesInvShapeTensor: false,
          Write_After_Damage: false,
          Frequency: 100,
          InitStep: 0,
        },
      ],
      outputKeys: {
        name: "Output Filename",
        Displacement: "Displacement",
        Force: "Force",
        Damage: "Damage",
        Partial_Stress: "Partial_Stress",
        Number_Of_Neighbors: "Number_Of_Neighbors",
        Contact_Force: "Contact_Force",
        Horizon: "Horizon",
        Model_Coordinates: "Model_Coordinates",
        Local_Angles: "Local_Angles",
        Coordinates: "Coordinates",
        Acceleration: "Acceleration",
        Temperature: "Temperature",
        Temperature_Change: "Temperature_Change",
        Force_Density: "Force_Density",
        External_Force_Density: "External_Force_Density",
        Damage_Model_Data: "Damage_Model_Data",
        Velocity_Gradient: "Velocity_Gradient",
        PiolaStressTimesInvShapeTensor: "PiolaStressTimesInvShapeTensor",
        Write_After_Damage: "Write After Damage",
        Frequency: "Output Frequency",
        InitStep: "Initial Output Step",
      },
      // Solver
      solvertype: ["Verlet", "NOXQuasiStatic"],
      peridgimPreconditioner: ["Full Tangent", "Block 3x3", "None"],
      nonlinearSolver: ["Line Search Based"],
      directionMethod: ["Newton", "NonlinearCG"],
      jacobianOperator: ["Matrix-Free", ""],
      preconditioner: ["User Defined", "None"],
      lineSearchMethod: ["Polynomial"],
      filetype: ["yaml", "xml"],
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
        stopBeforeDamageInitation: false,
        adaptivetimeStepping: false,
        adapt: {
          stableStepDifference: 4,
          maximumBondDifference: 4,
          stableBondDifference: 1,
        },
        filetype: "yaml",
      },
      solverKeys: {
        verbose: "Verbose",
        initialTime: "Initial Time",
        finalTime: "Final Time",
        solvertype: "Solvertype",
        fixedDt: "Fixed dt",
        safetyFactor: "Safety Factor",
        numericalDamping: "Numerical Damping",
        peridgimPreconditioner: "Peridgim Preconditioner",
        nonlinearSolver: "Nonlinear Solver",
        numberOfLoadSteps: "Number of Load Steps",
        maxSolverIterations: "Max Solver Iterations",
        relativeTolerance: "Relative Tolerance",
        maxAgeOfPrec: "Max Age Of Prec",
        directionMethod: "Direction Method",
        newton: {
          jacobianOperator: "Jacobian Operator",
          preconditioner: "Preconditioner",
        },
        lineSearchMethod: "Line Search Method",
        verletSwitch: "Switch to Verlet",
        verlet: {
          safetyFactor: "Safety Factor",
          numericalDamping: "Numerical Damping",
          outputFrequency: "Output Frequency",
        },
        stopAfterDamageInitation: "Stop after damage initation",
        stopBeforeDamageInitation: "Stop before damage initation",
        adaptivetimeStepping: "Adaptive Time Stepping",
        adapt: {
          stableStepDifference: "Stable Step Difference",
          maximumBondDifference: "Maximum Bond Difference",
          stableBondDifference: "Stable Bond Difference",
        },
      },
      // Job
      job: {
        cluster: "None",
        tasks: 1,
        time: "40:00:00",
        // user: 'hess_ja',
        account: "2263032",
        // mail: 'jan-timo.hesse@dlr.de',
      },
      cluster: ["Cara", "None"], //'FA-Cluster',

      url: "https://perihub-api.fa-services.intra.dlr.de/",
      trameUrl: "https://perihub-trame-api.fa-services.intra.dlr.de/",
      textOutput: "",
      pointString: [1, 0, 0],
      filteredPointString: [1, 0, 0],
      blockIdString: [1],
      filteredBlockIdString: [1],
      bondFilterPoints: [
        {
          bondFilterPointsId: 1,
          bondFilterPointString: [],
          // bondFilterPolyString: []
        },
      ],
      resolution: 6,
      dx_value: 0.1,
      radius: 0.2,
      multiplier: 1,
      snackbar: false,
      message: "Messsages",
      errorMessage: "Error",
      status: {
        created: false,
        submitted: false,
        results: false,
      },
      authToken: "",
      modelLoading: false,
      textLoading: false,
      resultsLoading: false,
      dataJson: "",
      colors: "",
      modelImg: DogboneImage,
      vtkFile: "",
      dialog: false,
      dialogGetImage: false,
      dialogGetImagePython: false,
      getImageOutput: "Output1",
      getImageVariable: [
        "Displacement",
        "Force",
        "Damage",
        "Partial_StressX",
        "Partial_StressY",
        "Partial_StressZ",
        "Number_Of_Neighbors",
      ],
      getImageVariableSelected: "Displacement",
      getImageAxis: ["Magnitude", "X", "Y", "Z"],
      getImageAxisSelected: "Magnitude",
      getImageDisplFactor: 20,
      getImageMarkerSize: 16,
      dialogGetG1c: false,
      getG1cOutput: "Output1",
      getG1cFrequency: 10,
      dialogShowResults: false,
      dialogGetPlot: false,
      dialogDeleteData: false,
      dialogDeleteModel: false,
      dialogDeleteCookies: false,
      dialogDeleteUserData: false,
      dialogGcode: false,
      dialogError: false,
      errors: [],
      gcodeFile: {},
      gcodeDiscretization: 1,
      plotRawData: "",
      plotData: [
        {
          name: "Displacement",
          x: [1, 2, 3, 4],
          y: [10, 15, 20, 17],
          type: "scatter",
        },
        {
          name: "Force",
          x: [1, 2, 3, 4],
          y: [10, 15, 5, 17],
          type: "scatter",
        },
      ],
      plotLayout: {
        // title: 'this.model.modelNameSelected',
        showlegend: true,
        // margin: { t: 50 },
        hovermode: "compare",
        bargap: 0,
        xaxis: {
          showgrid: true,
          zeroline: true,
          color: "white",
        },
        yaxis: {
          showgrid: true,
          zeroline: true,
          color: "white",
        },
        xaxis2: {
          showgrid: false,
          zeroline: false,
        },
        yaxis2: {
          showgrid: true,
          zeroline: false,
        },
        plot_bgcolor: "#2D2D2D",
        paper_bgcolor: "#2D2D2D",
        font: {
          color: "white",
        },
        modebar: {
          color: "white",
          // color: "#6E6E6E"
        },
      },
      plotOptions: {
        scrollZoom: true,
        setBackground: "black",
      },
      logInterval: null,
      statusInterval: null,
      monitorToggle: false,
      viewId: 0,
      panel: [0],

      resultPort: null,
      port: "",
      showResultsOutputName: "Output1",

      rules: {
        required: (value) => !!value || value == 0 || "Required",
        name: (value) => {
          const pattern = /^[A-Za-z0-9_]{1,15}/;
          return pattern.test(value) || "Invalid name";
        },
        posFloat: (value) => {
          const pattern = /^((?!0)|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
          return pattern.test(value) || "Invalid number";
        },
        float: (value) => {
          const pattern = /^((?!0)|[-]|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
          return pattern.test(value) || "Invalid number";
        },
        int: (value) => {
          const pattern = /^[-]{0,1}(?<!\.)\d+(?!\.)$/;
          return pattern.test(value) || "Invalid number";
        },
      },
    };
  },
  filters: {
    number(value) {
      return value.toFixed(2);
    },
  },
  methods: {
    highlighter(code) {
      return highlight(code, languages.js); // languages.<insert language> to return html with markup
    },

    async viewInputFile(loadFile) {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "viewInputFile",
        params: {
          model_name: this.model.modelNameSelected,
          own_mesh: this.model.ownMesh,
          FileType: this.solver.filetype,
        },
        method: "GET",
        headers: headersList,
      };

      await axios.request(reqOptions).then((response) => {
        this.textOutput = response.data;
        if (loadFile) {
          this.loadYamlString(this.textOutput);
        }
      });
    },
    async generateModel() {
      // this.snackbar=true
      // this.message = JSON.parse("{\"Param\":" + "{\"Material\": " + JSON.stringify(this.materials)+",\n" +
      //                                     "\"Solver\": " + JSON.stringify(this.solver)+",\n" +
      //                                     "\"Output\": " + JSON.stringify(this.outputs) + "}}")
      if (this.checkInputs()) {
        if (
          (this.model.modelNameSelected == "CompactTension") &
          !this.model.ownModel
        ) {
          this.model.height = this.model.length * 1.25;
          console.log(this.model.height);
        }

        let headersList = {
          "Cache-Control": "no-cache",
          Authorization: this.authToken,
          // 'Access-Control-Allow-Origin': '*'
        };
        let reqOptions = {
          url: this.url + "generateModel",
          params: { model_name: this.model.modelNameSelected },
          data: JSON.parse(
            '{"model": ' +
              JSON.stringify(this.model) +
              ",\n" +
              '"materials": ' +
              JSON.stringify(this.materials) +
              ",\n" +
              '"damages": ' +
              JSON.stringify(this.damages) +
              ",\n" +
              '"blocks": ' +
              JSON.stringify(this.blocks) +
              ",\n" +
              '"contact": ' +
              JSON.stringify(this.contact) +
              ",\n" +
              '"boundaryConditions": ' +
              JSON.stringify(this.boundaryConditions) +
              ",\n" +
              '"bondFilters": ' +
              JSON.stringify(this.bondFilters) +
              ",\n" +
              '"computes": ' +
              JSON.stringify(this.computes) +
              ",\n" +
              '"outputs": ' +
              JSON.stringify(this.outputs) +
              ",\n" +
              '"solver": ' +
              JSON.stringify(this.solver) +
              "}"
          ),
          method: "POST",
          headers: headersList,
        };
        console.log(
          JSON.parse(
            '{"model": ' +
              JSON.stringify(this.model) +
              ",\n" +
              '"materials": ' +
              JSON.stringify(this.materials) +
              ",\n" +
              '"damages": ' +
              JSON.stringify(this.damages) +
              ",\n" +
              '"blocks": ' +
              JSON.stringify(this.blocks) +
              ",\n" +
              '"contact": ' +
              JSON.stringify(this.contact) +
              ",\n" +
              '"boundaryConditions": ' +
              JSON.stringify(this.boundaryConditions) +
              ",\n" +
              '"bondFilters": ' +
              JSON.stringify(this.bondFilters) +
              ",\n" +
              '"computes": ' +
              JSON.stringify(this.computes) +
              ",\n" +
              '"outputs": ' +
              JSON.stringify(this.outputs) +
              ",\n" +
              '"solver": ' +
              JSON.stringify(this.solver) +
              "}"
          )
        );
        if (this.model.ownModel == false) {
          this.modelLoading = true;
        }
        this.textLoading = true;
        await axios
          .request(reqOptions)
          .then((response) => (this.message = response.data))
          .catch((error) => {
            if (error.response.status == 422) {
              let message = "";
              for (let i in error.response.data.detail) {
                message += error.response.data.detail[i].loc[1] + " ";
                message += error.response.data.detail[i].loc[2] + ", ";
                message += error.response.data.detail[i].loc[3] + ", ";
                message += error.response.data.detail[i].msg + "\n";
              }
              message = message.slice(0, -2);
              this.openErrorDialog(message);
            }
            this.modelLoading = false;
            this.textLoading = false;
            // this.message = error,
            console.log(error.response.data);
            return;
          });
        this.snackbar = true;
        if (this.message.includes("has been created")) {
          this.viewInputFile(false);
          if (this.model.ownModel == false) {
            this.viewPointData();
          }
        }
        this.modelLoading = false;
        this.textLoading = false;
        this.getStatus();
      }
    },
    async generateMesh() {
      let headersList = {
        "Cache-Control": "no-cache",
        "Content-Type": "multipart/form-data",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "generateMesh",
        params: {
          model_name: this.model.modelNameSelected,
          Param: JSON.stringify(this.micofam),
        },
        method: "GET",
        headers: headersList,
      };

      this.modelLoading = true;

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));

      this.snackbar = true;

      if (this.message == "Mesh generated") {
        this.model.ownModel = true;
        this.model.translated = true;
        // this.model.modelNameSelected = this.message

        var files;
        this.translateModel(files, "inp", false);
        // this.viewInputFile(true)
        // this.loadYamlString(this.textOutput)
        // this.viewPointData()

        // this.modelLoading = false
        this.modelLoading = false;

        this.snackbar = true;
      } else {
        this.modelLoading = false;
      }
      this.getStatus();
      // let headersList = {
      // 'Cache-Control': 'no-cache',
      // 'accept': 'application/json',
      // 'Content-Type': 'multipart/form-data'
      // }
      // let reqOptions = {
      //   url: "https://fa-jenkins2:5000/1/PyCODAC/api/micofam/{zip}",
      //   // data: JSON.parse(JSON.stringify(this.micofam)),
      //   method: "PATCH",
      //   responseType: 'blob',
      //   // headers: headersList,
      // }
      // if(this.model.ownModel==false){
      //   this.modelLoading = true
      // }
      // this.textLoading = true
      // this.modelLoading = true
      // var zipFile
      // await axios.request(reqOptions)
      // .then((response) => {
      //     var fileURL = window.URL.createObjectURL(new Blob([response.data]));
      //     var fileLink = document.createElement('a');
      //     fileLink.href = fileURL;
      //     fileLink.setAttribute('download', this.model.modelNameSelected + '.zip');
      //     document.body.appendChild(fileLink);
      //     fileLink.click();
      // })
      // .catch((error) => {
      //   this.message = error
      //   this.snackbar = true
      // });
      // await axios.request(reqOptions).then(response => (zipFile = response.data))

      // var jsZip = require('jszip')
      // jsZip.loadAsync(zipFile).then(function (zip) {
      //   Object.keys(zip.files).forEach(function (filename) {
      //     zip.files[filename].async('string').then(function (fileData) {
      //       console.log(fileData) // These are your file contents
      //     })
      //   })
      // })

      // this.snackbar=true
      // this.viewInputFile(false)
      // if(this.model.ownModel==false){
      //   this.viewPointData()
      // this.modelLoading = false
      // }
      // this.textLoading = false
    },
    saveData() {
      const data =
        '{"model": ' +
        JSON.stringify(this.model, null, 2) +
        ",\n" +
        '"materials": ' +
        JSON.stringify(this.materials, null, 2) +
        ",\n" +
        '"damages": ' +
        JSON.stringify(this.damages, null, 2) +
        ",\n" +
        '"blocks": ' +
        JSON.stringify(this.blocks, null, 2) +
        ",\n" +
        '"contact": ' +
        JSON.stringify(this.contact, null, 2) +
        ",\n" +
        '"boundaryConditions": ' +
        JSON.stringify(this.boundaryConditions, null, 2) +
        ",\n" +
        '"bondFilters": ' +
        JSON.stringify(this.bondFilters, null, 2) +
        ",\n" +
        '"computes": ' +
        JSON.stringify(this.computes, null, 2) +
        ",\n" +
        '"outputs": ' +
        JSON.stringify(this.outputs, null, 2) +
        ",\n" +
        '"solver": ' +
        JSON.stringify(this.solver, null, 2) +
        ",\n" +
        '"job": ' +
        JSON.stringify(this.job, null, 2) +
        "}";
      var fileURL = window.URL.createObjectURL(
        new Blob([data], { type: "application/json" })
      );
      var fileLink = document.createElement("a");
      fileLink.href = fileURL;
      fileLink.setAttribute("download", this.model.modelNameSelected + ".json");
      document.body.appendChild(fileLink);
      fileLink.click();
    },
    readData() {
      this.$refs.fileInput.click();
    },
    uploadMesh() {
      this.$refs.multifileInput.click();
    },
    uploadSo() {
      this.$refs.multiSoInput.click();
    },
    onFilePicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      const fr = new FileReader();

      if (filetype == "application/json") {
        this.loadJsonFile(fr, files);
      } else if (files[0].name.includes(".yaml")) {
        this.loadYamlModel(fr, files);
      } else if (filetype == "text/xml") {
        this.loadXmlModel(fr, files);
      } else if (filetype == ".peridigm") {
        this.loadPeridigmModel(fr, files);
      } else if (files[0].name.includes(".gcode")) {
        this.gcodeFile = files;
        this.dialogGcode = true;
      } else {
        this.loadFeModel(files);
      }
    },
    onMultiFilePicked(event) {
      const files = event.target.files;
      const filetype = files[0].type;
      if (files.length <= 0) {
        return false;
      }

      this.modelLoading = true;
      this.uploadfiles(files);

      this.viewPointData();
      this.modelLoading = false;
      this.snackbar = true;
    },
    async uploadfiles(files) {
      // this.snackbar=true
      // this.message = JSON.parse("{\"Job\": " + JSON.stringify(this.job)+"}")
      const formData = new FormData();
      for (var i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      let headersList = {
        "Cache-Control": "no-cache",
        "Content-Type": "multipart/form-data",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "uploadfiles",
        params: { model_name: this.model.modelNameSelected },
        data: formData,
        method: "POST",
        headers: headersList,
      };

      this.message = "Files have been uploaded";
      await axios.request(reqOptions).catch((error) => {
        console.log(response);
        this.message = error;
        return;
      });
    },
    //return an array of values that match on a certain key
    getValues(obj, key) {
      var objects = [];
      for (var i in obj) {
        if (!obj.hasOwnProperty(i)) continue;
        if (typeof obj[i] == "object") {
          objects = objects.concat(this.getValues(obj[i], key));
        } else if (i == key) {
          objects.push(obj[i]);
        }
      }
      return objects;
    },
    getKeyByValue(object, value) {
      return Object.keys(object).find((key) => object[key] === value);
    },
    translateXMLtoYAML(xmlString) {
      var stringYAML = "Peridigm:\n";
      var splitString = xmlString.split("\n");
      for (var i = 0; i < splitString.length; i++) {
        if (
          !splitString[i].includes("</ParameterList>") &&
          !splitString[i].includes("<ParameterList>")
        ) {
          var partString = splitString[i].split('"');
          var spaces = splitString[i].split("<");

          if (partString.length > 3) {
            var temp_string = "";
            if (partString[3].includes("string")) {
              temp_string = '"' + partString[5] + '"';
            } else {
              temp_string = partString[5];
            }
            stringYAML += spaces[0] + partString[1] + ": " + temp_string + "\n";
          } else {
            if (partString.length != 1) {
              stringYAML += spaces[0] + partString[1] + ": \n";
            }
          }
        }
      }
      return stringYAML;
    },
    getValuesFromJson(
      paramObject,
      paramName,
      paramKeys,
      addFunction,
      removeFunction,
      id
    ) {
      var names = Object.keys(paramObject);
      if (paramName == "solver") {
        for (var i = 0; i < names.length; i++) {
          var key = this.getKeyByValue(paramKeys, names[i]);
          var subNames = Object.keys(paramObject[names[i]]);
          if (subNames.length != 0) {
            for (var j = 0; j < subNames.length; j++) {
              this[paramName]["solvertype"] = names[i];
              var key = this.getKeyByValue(paramKeys, subNames[j]);
              if (key == undefined) {
                console.log(
                  "Warning: " + subNames[j] + " is not supported yet"
                );
                continue;
              }
              console.log(subNames[j]);
              console.log(key);
              console.log(paramObject[names[i]][subNames[j]]);
              this[paramName][key] = paramObject[names[i]][subNames[j]];
            }
            continue;
          }
          if (key == undefined) {
            console.log("Warning: " + names[i] + " is not supported yet");
            continue;
          }
          // Object.assign(this[paramName][key], paramObject[names[i]])
          this[paramName][key] = paramObject[names[i]];
        }
      } else if (paramName == "outputs") {
        if (id.length >= 1) {
          if (this[paramName].length < id) {
            addFunction();
          }
          for (var i = 0; i < names.length; i++) {
            var key = this.getKeyByValue(paramKeys, names[i]);
            // console.log(key)
            // console.log(paramObject[names[i]])
            if ((key == undefined) & (names[i] != "Output Variables")) {
              console.log("Warning: " + names[i] + " is not supported yet");
              continue;
            } else {
              if (key == "name") {
                this[paramName][id - 1][key] = paramObject[names[i]]
                  .split("_")
                  .slice(-1)[0];
                continue;
              } else {
                this[paramName][id - 1][key] = paramObject[names[i]];
              }
              var subNames = Object.keys(paramObject[names[i]]);
              for (var j = 0; j < subNames.length; j++) {
                var key = this.getKeyByValue(paramKeys, subNames[j]);
                // console.log(key)
                // console.log(paramObject[names[i]][subNames[j]])
                if (key == undefined) {
                  console.log(
                    "Warning: subname " + subNames[j] + " is not supported yet"
                  );
                  continue;
                }
                this[paramName][id - 1][key] =
                  paramObject[names[i]][subNames[j]];
              }
            }
          }
          if (this[paramName].length > id) {
            for (var j = id; j < this[paramName].length; j++) {
              removeFunction(j);
            }
          }
        } else {
          for (var i = 0; i < names.length; i++) {
            var key = this.getKeyByValue(paramKeys, names[i]);
            if (key == undefined) {
              console.log("Warning: " + names[i] + " is not supported yet");
              continue;
            }
            if (key == "name") {
              this[paramName][0][key] = paramObject[names[i]]
                .split("_")
                .slice(-1)[0];
            } else {
              this[paramName][0][key] = paramObject[names[i]];
            }
            var subNames = Object.keys(paramObject[names[i]]);
            for (var j = 0; j < subNames.length; j++) {
              var key = this.getKeyByValue(paramKeys, subNames[j]);
              if (key == undefined) {
                console.log(
                  "Warning: " + subNames[j] + " is not supported yet"
                );
                continue;
              }
              Object.assign(
                this[paramName][0][key],
                paramObject[names[i]][subNames[j]]
              );
            }
          }
          if (this[paramName].length > 1) {
            for (var j = 1; j < this[paramName].length; j++) {
              removeFunction(j);
            }
          }
        }
      } else if (paramName == "boundaryConditions") {
        var numberOfItems = 0;
        // var filteredNames = []
        // for(var i = 0; i < names.length; i++) {
        //   if (Object.keys(paramObject[names[i]])[0].length>2){
        //     numberOfItems++
        //     filteredNames.push(names[i])
        //   }
        // }
        for (var i = 0; i < names.length; i++) {
          if (!names[i].includes("Node Set")) {
            if (this[paramName].length < numberOfItems + 1) {
              addFunction();
            }
            this[paramName][numberOfItems]["name"] = names[i];
            var subNames = Object.keys(paramObject[names[i]]);
            for (var j = 0; j < subNames.length; j++) {
              var key = this.getKeyByValue(paramKeys, subNames[j]);
              if (key == undefined) {
                console.log(
                  "Warning: " + subNames[j] + " is not supported yet"
                );
                continue;
              }
              // Object.assign(this[paramName][i][key], paramObject[names[i]][subNames[j]])
              // var temp =
              this[paramName][numberOfItems][key] =
                paramObject[names[i]][subNames[j]];
              // Object.assign(this[paramName][i][key], temp)
            }
            numberOfItems++;
          }
        }
        if (this[paramName].length > numberOfItems) {
          for (var j = numberOfItems; j < this[paramName].length; j++) {
            removeFunction(j);
          }
        }
      } else {
        for (var i = 0; i < names.length; i++) {
          if (this[paramName].length < i + 1) {
            addFunction();
          }
          this[paramName][i]["name"] = names[i];
          var subNames = Object.keys(paramObject[names[i]]);
          for (var j = 0; j < subNames.length; j++) {
            var key = this.getKeyByValue(paramKeys, subNames[j]);
            if (subNames[j] == "Number of properties") {
              let numberOfProps = parseInt(paramObject[names[i]][subNames[j]]);
              if (this.materials[i].properties.length < numberOfProps) {
                while (this.materials[i].properties.length != numberOfProps) {
                  this.addProp(i);
                }
              }
              if (this.materials[i].properties.length > numberOfProps) {
                for (
                  var j = numberOfProps;
                  j < this.materials[i].properties.length;
                  j++
                ) {
                  this.removeProp(i, j);
                }
              }
              continue;
            }
            if (subNames[j].indexOf("Prop_") !== -1) {
              id = parseInt(subNames[j].split("_")[1]);
              this.materials[i].properties[id - 1].value =
                paramObject[names[i]][subNames[j]];
              continue;
            }
            if (key == undefined) {
              console.log("Warning: " + subNames[j] + " is not supported yet");
              continue;
            }
            if (subNames[j] == "Horizon") {
              if (
                parseFloat(paramObject[names[i]][subNames[j]]) ==
                paramObject[names[i]][subNames[j]]
              ) {
                this.model.horizon = paramObject[names[i]][subNames[j]];
              } else {
                this.model.horizon = -1.0;
              }
            }
            this[paramName][i][key] = paramObject[names[i]][subNames[j]];
          }
        }
        if (this[paramName].length > names.length) {
          for (var j = names.length; j < this[paramName].length; j++) {
            removeFunction(j);
          }
        }
      }
    },
    loadJsonFile(fr, files) {
      this.model.ownMesh = false;
      this.model.ownModel = false;
      this.model.translated = false;

      fr.onload = (e) => {
        const result = JSON.parse(e.target.result);
        for (var j = 0; j < Object.keys(result).length; j++) {
          var paramName = Object.keys(result)[j];
          if (Array.isArray(result[paramName])) {
            this[paramName] = [...result[paramName]];
          } else {
            this[paramName] = { ...result[paramName] };
          }
          // this[paramName] = { ...result[paramName] };
        }
      };
      fr.readAsText(files.item(0));
    },
    loadYamlModel(fr, files) {
      this.model.ownMesh = false;
      this.model.ownModel = true;
      this.model.translated = false;

      this.model.modelNameSelected = files[0].name.split(".")[0];

      fr.onload = (e) => {
        const yaml = e.target.result;
        this.loadYamlString(yaml);
      };
      fr.readAsText(files.item(0));
    },
    loadXmlModel(fr, files) {
      this.model.ownMesh = false;
      this.model.ownModel = true;
      this.model.translated = false;

      this.model.modelNameSelected = files[0].name.split(".")[0];

      fr.onload = (e) => {
        const xml = e.target.result;
        var yaml = this.translateXMLtoYAML(xml);
        this.loadYamlString(yaml);
      };
      fr.readAsText(files.item(0));
    },
    async loadFeModel(files) {
      this.model.ownMesh = true;
      this.model.ownModel = true;
      this.model.translated = true;

      this.modelLoading = true;
      this.textLoading = true;

      if (files.length <= 0) {
        return false;
      }

      if (await this.checkFeSize(files)) {
        this.model.modelNameSelected = files[0].name.split(".")[0];
        const filetype = files[0].name.split(".")[1];

        await this.translateModel(files, filetype, true);
      } else {
        this.modelLoading = false;
        this.textLoading = false;
      }
    },
    async loadGcodeModel() {
      this.dialogGcode = false;
      this.model.ownMesh = false;
      this.model.ownModel = true;
      // this.model.translated = true;

      this.modelLoading = true;
      // this.textLoading = true;

      if (this.gcodeFile.length <= 0) {
        return false;
      }

      this.model.modelNameSelected = this.gcodeFile[0].name.split(".")[0];
      const filetype = this.gcodeFile[0].name.split(".")[1];

      await this.translatGcode(this.gcodeFile, true);
    },
    async checkFeSize(files) {
      let headersList = {
        Authorization: this.authToken,
      };
      let reqOptions = {
        url: this.url + "getMaxFeSize",
        method: "GET",
        headers: headersList,
      };

      var allowedFeSize = 0;
      await axios
        .request(reqOptions)
        .then((response) => (allowedFeSize = response.data));

      if (allowedFeSize > files[0].size) {
        return true;
      } else {
        this.message =
          "The file size (" +
          this.formatBytes(files[0].size) +
          ") is larger than the allowed " +
          this.formatBytes(allowedFeSize);
        this.snackbar = true;
        return false;
      }
    },
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) {
        return "0 Bytes";
      }
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
    },
    async translateModel(files, filetype, upload) {
      const formData = new FormData();
      if (upload) {
        await this.uploadfiles(files);
      }
      let headersList = {
        "Cache-Control": "no-cache",
        "Content-Type": "multipart/form-data",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "translateModel",
        params: {
          model_name: this.model.modelNameSelected,
          file_type: filetype,
        },
        method: "POST",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));

      this.viewInputFile(true);
      // this.loadYamlString(this.textOutput)
      this.viewPointData();

      this.modelLoading = false;
      this.textLoading = false;

      this.snackbar = true;
    },
    async translatGcode(files, upload) {
      const formData = new FormData();
      if (upload) {
        await this.uploadfiles(files);
      }
      let headersList = {
        "Cache-Control": "no-cache",
        "Content-Type": "multipart/form-data",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "translatGcode",
        params: {
          model_name: this.model.modelNameSelected,
          discretization: this.gcodeDiscretization,
        },
        method: "POST",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));

      // this.viewInputFile(true);
      // this.loadYamlString(this.textOutput)
      this.viewPointData();

      this.modelLoading = false;
      // this.textLoading = false;

      this.snackbar = true;
    },
    loadYamlString(yaml) {
      var convert = require("js-yaml");
      var json = convert.load(yaml);
      // this.message = json
      // this.snackbar =true
      var names = Object.keys(json.Peridigm);
      for (var i = 0; i < names.length; i++) {
        var Param = json.Peridigm[names[i]];
        switch (names[i].replace(/[0-9]/g, "")) {
          case "Materials":
            for (var j = 0; j < this.materials.length; j++) {
              this.materials[j].poissonsRatio = null;
              this.materials[j].bulkModulus = null;
              this.materials[j].shearModulus = null;
              this.materials[j].youngsModulus = null;
            }
            this.getValuesFromJson(
              Param,
              "materials",
              this.materialKeys,
              this.addMaterial,
              this.removeMaterial
            );
            break;
          case "Damage Models":
            this.getValuesFromJson(
              Param,
              "damages",
              this.damageKeys,
              this.addDamage,
              this.removeDamage
            );
            break;
          case "Blocks":
            this.getValuesFromJson(
              Param,
              "blocks",
              this.blockKeys,
              this.addBlock,
              this.removeBlock
            );
            break;
          case "Contact":
            console.log("Contact import not supported yet!");
            // this.getValuesFromJson(
            //   Param,
            //   "contact",
            //   this.blockKeys,
            //   this.addC,
            //   this.removeBlock
            // );
            break;
          case "Boundary Conditions":
            this.getValuesFromJson(
              Param,
              "boundaryConditions",
              this.boundaryKeys,
              this.addCondition,
              this.removeCondition
            );
            break;
          case "Bond Filters":
            this.getValuesFromJson(
              Param,
              "bondFilters",
              this.bondFilterKeys,
              this.addBondFilter,
              this.removeBondFilter
            );
            break;
          case "Compute Class Parameters":
            this.getValuesFromJson(
              Param,
              "computes",
              this.computeKeys,
              this.addCompute,
              this.removeOutput
            );
            break;
          case "Output":
            for (var j = 0; j < this.outputs.length; j++) {
              this.outputs[j].Displacement = false;
              this.outputs[j].Force = false;
              this.outputs[j].Damage = false;
              this.outputs[j].Partial_Stress = false;
              this.outputs[j].Number_Of_Neighbors = false;
              this.outputs[j].Contact_Force = false;
              this.outputs[j].Horizon = false;
              this.outputs[j].Model_Coordinates = false;
              this.outputs[j].Local_Angles = false;
              this.outputs[j].Coordinates = false;
              this.outputs[j].Acceleration = false;
              this.outputs[j].Temperature = false;
              this.outputs[j].Temperature_Change = false;
              this.outputs[j].Force_Density = false;
              this.outputs[j].External_Force_Density = false;
              this.outputs[j].Damage_Model_Data = false;
              this.outputs[j].Velocity_Gradient = false;
              this.outputs[j].PiolaStressTimesInvShapeTensor = false;
              this.outputs[j].Write_After_Damage = false;
            }
            this.getValuesFromJson(
              Param,
              "outputs",
              this.outputKeys,
              this.addOutput,
              this.removeOutput,
              names[i].replace(/\D/g, "")
            );
            break;
          case "Solver":
            this.getValuesFromJson(Param, "solver", this.solverKeys);
            break;
        }
      }
    },
    switchModels() {
      this.model.ownMesh = false;
      this.model.ownModel = false;
      this.model.translated = false;
    },
    async resetData() {
      const jsonFile = {};
      switch (this.model.modelNameSelected) {
        case "GICmodel":
          Object.assign(jsonFile, GICmodelFile);
          break;
        case "GIICmodel":
          Object.assign(jsonFile, GIICmodelFile);
          break;
        case "DCBmodel":
          Object.assign(jsonFile, DCBmodelFile);
          break;
        case "Dogbone":
          Object.assign(jsonFile, DogboneFile);
          break;
        case "Kalthoff-Winkler":
          Object.assign(jsonFile, KalthoffWinklerFile);
          break;
        case "PlateWithHole":
          Object.assign(jsonFile, PlateWithHoleFile);
          break;
        case "CompactTension":
          Object.assign(jsonFile, CompactTensionFile);
          break;
        case "Smetana":
          Object.assign(jsonFile, SmetanaFile);
          break;
        default:
          return;
      }

      // for(var i = 0; i < Object.keys(this.jsonFile).length; i++) {
      // var name = Object.keys(this.jsonFile)[i]
      // if (name!='Param'){
      //   this.model[name] = this.jsonFile[name];
      // }
      // else{
      // var param = result[i]
      // console.log(jsonFile);
      // console.log(Object.keys(jsonFile).length)
      for (var i = 0; i < Object.keys(jsonFile).length; i++) {
        var paramName = Object.keys(jsonFile)[i];
        // console.log(i)
        if ((paramName != "model") & (paramName != "solver")) {
          // console.log(paramName);
          // console.log(this[paramName].length)
          // console.log(jsonFile[paramName].length)
          // console.log(this[paramName])
          // console.log(jsonFile[paramName])
          if (this[paramName].length > jsonFile[paramName].length) {
            for (
              var j = this[paramName].length;
              j >= jsonFile[paramName].length;
              j--
            ) {
              // for(var j = jsonFile[paramName].length; j < this[paramName].length; j++) {
              this[paramName].splice(j, 1);
              // console.log('Remove'+ j)
            }
          }
          if (this[paramName].length < jsonFile[paramName].length) {
            for (
              var j = this[paramName].length;
              j < jsonFile[paramName].length;
              j++
            ) {
              this[paramName].push({});
            }
          }
        }
        // console.log(this[paramName]);
        // console.log(jsonFile[paramName]);
        // this[paramName] = [...jsonFile[paramName]];
        this.$set(this, paramName, jsonFile[paramName]);
        // Object.assign(this[paramName], jsonFile[paramName]);
      }
      // }
      // }
    },
    // saveCurrentData() {
    // this.$store.commit('saveModelName', this.model.modelNameSelected);
    // this.$cookie.set('panel', JSON.stringify(this.panel), { expires: '1M' }, '/app');
    // this.$cookie.set('ownModel', this.model.ownModel, { expires: '1M' }, '/app');
    // this.$cookie.set('translated', this.model.translated, { expires: '1M' }, '/app');
    // const data = "{\"modelNameSelected\":\"" + this.model.modelNameSelected + "\",\n" +
    //               "\"length\":" + this.model.length + ",\n" +
    //               "\"width\":" + this.model.width + ",\n" +
    //               "\"height\":" + this.model.height + ",\n" +
    //               "\"height2\":" + this.model.height2 + ",\n" +
    //               "\"discretization\":" + this.model.discretization + ",\n" +
    //               "\"twoDimensional\":" + this.model.twoDimensional + ",\n" +
    //               "\"rotatedAngles\":" + this.model.rotatedAngles + ",\n" +
    //               "\"angles\":[" + this.model.angles + "]}";
    // this.$cookie.set('data', data, { expires: '1M' }, '/app');
    // this.jsonToCookie("materials", true)
    // this.jsonToCookie("damages")
    // this.jsonToCookie("blocks", true)
    // this.jsonToCookie("boundaryConditions")
    // this.jsonToCookie("computes")
    // this.jsonToCookie("outputs")
    // this.jsonToCookie("solver")
    // this.jsonToCookie("job")
    // },
    // jsonToCookie(name, split = false) {
    //   if(!split){
    //     const data = "{\"" + name + "\": " + JSON.stringify(this[name])+"}";
    //     this.$cookie.set(name, data, { expires: '1M' }, '/app');
    //   }
    //   else{
    //     for(var i = this[name].length; i<100; i++){
    //       this.$cookie.delete(name+i)
    //     }
    //     for(var id = 0; id < this[name].length; id++) {
    //       const subdata = "{\"" + name + id + "\": " + JSON.stringify(this[name][id])+"}";
    //       this.$cookie.set(name + id, subdata, { expires: '1M' }, '/app');
    //     }
    //   }
    // },
    // cookieToJson(name, split = false) {
    //   if(!split){
    //     const data = JSON.parse(this.$cookie.get(name));
    //     if(data==null) return
    //     for(var i = 0; i < Object.keys(data).length; i++) {
    //       var name = Object.keys(data)[i]
    //       this[name] = data[name];
    //     }
    //   }
    //   else{
    //     for(var id = 0; id < 100; id++) {
    //       const subdata = JSON.parse(this.$cookie.get(name + id));
    //       if(subdata==null) break
    //       this[name][id] = subdata[name + id]
    //     }
    //   }
    // },
    async viewPointData() {
      this.modelLoading = true;
      this.viewId = 1;

      await this.getPointDataAndUpdateDx();

      this.radius = this.dx_value.toFixed(2);
      this.updatePoints();

      this.modelLoading = false;
      this.$refs.view.resetCamera();
    },
    filterPointData() {
      var idx = 0;
      this.filteredBlockIdString = [];
      this.filteredPointString = [];
      for (var i = 0; i < this.blockIdString.length; i++) {
        if (
          this.blocks[parseInt(this.blockIdString[i] * this.blocks.length - 1)]
            .show
        ) {
          this.filteredBlockIdString[idx] = this.blockIdString[i];
          for (var j = 0; j < 3; j++) {
            this.filteredPointString[idx * 3 + j] =
              this.pointString[i * 3 + j] * this.multiplier;
          }
          idx += 1;
        }
      }
    },
    cross(a1, a2, a3, b1, b2, b3) {
      return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1];
    },
    vectorLength(a1, a2, a3) {
      return Math.sqrt(a1 * a1 + a2 * a2 + a3 * a3);
    },
    getVectorNorm(a1, a2, a3) {
      const bottomLength = Math.abs(this.vectorLength(a1, a2, a3));
      const normx = a1 / bottomLength;
      const normy = a2 / bottomLength;
      const normz = a3 / bottomLength;
      return [normx, normy, normz];
    },
    showHideBondFilters() {
      // this.bondFilterPolyString = []
      // let bondFilterPolyString = []
      this.bondFilterPoints = [];

      for (var i = 0; i < this.bondFilters.length; i++) {
        let bondFilterPointString = [];
        const bondFilter = this.bondFilters[i];
        if (bondFilter.show) {
          const nx = parseFloat(bondFilter.normalX);
          const ny = parseFloat(bondFilter.normalY);
          const nz = parseFloat(bondFilter.normalZ);

          if (bondFilter.type == "Disk") {
            const cx = parseFloat(bondFilter.centerX);
            const cy = parseFloat(bondFilter.centerY);
            const cz = parseFloat(bondFilter.centerZ);
            const radius = parseFloat(bondFilter.radius);

            let crossVector1 = this.cross(nx, ny, nz, 1.0, 0.0, 0.0);
            let crossVector2 = this.cross(nx, ny, nz, 0.0, 1.0, 0.0);
            let crossVector3 = this.cross(nx, ny, nz, -1.0, 0.0, 0.0);
            let crossVector4 = this.cross(nx, ny, nz, 0.0, -1.0, 0.0);

            let normVector1 = this.getVectorNorm(
              crossVector1[0],
              crossVector1[1],
              crossVector1[2]
            );
            let normVector2 = this.getVectorNorm(
              crossVector2[0],
              crossVector2[1],
              crossVector2[2]
            );
            let normVector3 = this.getVectorNorm(
              crossVector3[0],
              crossVector3[1],
              crossVector3[2]
            );
            let normVector4 = this.getVectorNorm(
              crossVector4[0],
              crossVector4[1],
              crossVector4[2]
            );

            const point1x = cx + normVector1[0] * radius;
            const point1y = cy + normVector1[1] * radius;
            const point1z = cz + normVector1[2] * radius;
            const point2x = cx + normVector2[0] * radius;
            const point2y = cy + normVector2[1] * radius;
            const point2z = cz + normVector2[2] * radius;
            const point3x = cx + normVector3[0] * radius;
            const point3y = cy + normVector3[1] * radius;
            const point3z = cz + normVector3[2] * radius;
            const point4x = cx + normVector4[0] * radius;
            const point4y = cy + normVector4[1] * radius;
            const point4z = cz + normVector4[2] * radius;

            bondFilterPointString.push(point1x, point1y, point1z);
            bondFilterPointString.push(point2x, point2y, point2z);
            bondFilterPointString.push(point3x, point3y, point3z);
            bondFilterPointString.push(point4x, point4y, point4z);
          } else {
            const lx = parseFloat(bondFilter.lowerLeftCornerX);
            const ly = parseFloat(bondFilter.lowerLeftCornerY);
            const lz = -parseFloat(bondFilter.lowerLeftCornerZ);
            const bx = parseFloat(bondFilter.bottomUnitVectorX);
            const by = parseFloat(bondFilter.bottomUnitVectorY);
            const bz = parseFloat(bondFilter.bottomUnitVectorZ);
            const bl = parseFloat(bondFilter.bottomLength);
            const sl = parseFloat(bondFilter.sideLength);

            const point1x = lx;
            const point1y = ly;
            const point1z = lz;

            let [normx, normy, normz] = this.getVectorNorm(bx, by, bz);

            const point2x = lx + normx * bl;
            const point2y = ly + normy * bl;
            const point2z = lz + normz * bl;

            let crossVector = this.cross(nx, ny, nz, bx, by, bz);

            let normVector = this.getVectorNorm(
              crossVector[0],
              crossVector[1],
              crossVector[2]
            );

            const point4x = lx + normVector[0] * sl;
            const point4y = ly + normVector[1] * sl;
            const point4z = lz + normVector[2] * sl;

            const point3x = point2x + normVector[0] * sl;
            const point3y = point2y + normVector[1] * sl;
            const point3z = point2z + normVector[2] * sl;

            bondFilterPointString.push(point1x, point1y, point1z);
            bondFilterPointString.push(point2x, point2y, point2z);
            bondFilterPointString.push(point3x, point3y, point3z);
            bondFilterPointString.push(point4x, point4y, point4z);

            // bondFilterPolyString.push(4, 0, 1, 3, 2)
          }
        }
        if (this.bondFilterPoints.length < i + 1) {
          this.bondFilterPoints.push({
            bondFilterPointsId: i + 1,
            bondFilterPointString: [],
          });
        }
        this.bondFilterPoints[i].bondFilterPointString = bondFilterPointString;

        // this.bondFilterPoints[i].bondFilterPolyString = bondFilterPolyString
      }
    },
    updatePoints() {
      this.modelLoading = true;
      if (this.radius <= 0.2) {
        this.multiplier = (1 - this.radius / 0.5) * 30;
        this.filterPointData();
      } else {
        this.multiplier = 1;
        this.filterPointData();
      }
      this.modelLoading = false;
    },
    async getPointDataAndUpdateDx() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };
      let reqOptions = {
        url: this.url + "getPointData",
        params: {
          model_name: this.model.modelNameSelected,
          own_mesh: this.model.owMmesh,
        },
        method: "GET",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then(
          (response) => (
            (this.pointString = response.data[0].split(",")),
            (this.blockIdString = response.data[1].split(","))
          )
        )
        .catch(
          (error) => (
            (this.modelLoading = false),
            (this.message = error),
            (this.snackbar = true)
          )
        );

      if (!this.model.ownModel) {
        this.dx_value =
          this.model.height / (2 * parseInt(this.model.discretization / 2) + 1);
      } else {
        this.dx_value = Math.hypot(
          parseFloat(this.pointString[3]) - parseFloat(this.pointString[0]),
          parseFloat(this.pointString[4]) - parseFloat(this.pointString[1]),
          parseFloat(this.pointString[5]) - parseFloat(this.pointString[2])
        );
      }

      // if (this.model.modelNameSelected == "Smetana") {
      //   var blockIdInt = this.blockIdString.map(Number);
      //   let numberOfBlocks = Math.max(...blockIdInt);
      //   for (var i = 0; i < numberOfBlocks; i++) {
      //     if (this.blocks.length < i + 1) {
      //       this.addBlock();
      //     }
      //   }
      //   if (this.blocks.length > numberOfBlocks) {
      //     for (var j = numberOfBlocks; j < this.blocks.length; j++) {
      //       this.removeBlock(j);
      //     }
      //   }
      // }
    },
    // async copyModelToCluster() {
    //   let headersList = {
    //   'Cache-Control': 'no-cache'
    //   }
    //   let reqOptions = {
    //     url: this.url + "copyModelToCluster",
    //     params: {model_name: this.model.modelNameSelected,
    //             Cluster: this.job.cluster},
    //     method: "GET",
    //     headers: headersList,
    //   }
    //   this.loading = true
    //   await axios.request(reqOptions).then(response => (this.message = response.data))
    //   this.loading = false
    //   this.snackbar=true
    // },
    async runModel() {
      // this.snackbar=true
      // this.message = JSON.parse("{\"Job\": " + JSON.stringify(this.job)+"}")
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "runModel",
        params: {
          model_name: this.model.modelNameSelected,
          FileType: this.solver.filetype,
        },
        data: JSON.parse(
          '{"model": ' +
            JSON.stringify(this.model) +
            ",\n" +
            '"materials": ' +
            JSON.stringify(this.materials) +
            ",\n" +
            '"blocks": ' +
            JSON.stringify(this.blocks) +
            ",\n" +
            '"boundaryConditions": ' +
            JSON.stringify(this.boundaryConditions) +
            ",\n" +
            '"outputs": ' +
            JSON.stringify(this.outputs) +
            ",\n" +
            '"solver": ' +
            JSON.stringify(this.solver) +
            "}"
        ),
        method: "PUT",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data))
        .catch((error) => {
          let message = "";
          if (error.response.status == 422) {
            for (let i in error.response.data.detail) {
              message += error.response.data.detail[i].loc[1] + " ";
              message += error.response.data.detail[i].loc[2] + ", ";
              message += error.response.data.detail[i].loc[3] + ", ";
              message += error.response.data.detail[i].msg + "\n";
            }
            message = message.slice(0, -2);
          } else {
            message = error.response.data.detail;
          }
          this.openErrorDialog(message);
          // this.message = error,
          console.log(error.response.data);
          return;
        });
      this.getLogFile();
      this.snackbar = true;
      this.monitorStatus(true);
    },
    async getStatus() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getStatus",
        params: {
          model_name: this.model.modelNameSelected,
          own_model: this.model.ownModel,
          Cluster: this.job.cluster,
        },
        method: "GET",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.status = response.data));
      if (this.status.results) {
        clearInterval(this.statusInterval);
      }
    },
    async cancelJob() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "cancelJob",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
        },
        method: "PUT",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));
      this.snackbar = true;
      this.monitorStatus(false);
    },
    saveModel() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getModel",
        params: { model_name: this.model.modelNameSelected },
        method: "GET",
        responseType: "blob",
        headers: headersList,
      };

      axios
        .request(reqOptions)
        .then((response) => {
          var fileURL = window.URL.createObjectURL(new Blob([response.data]));
          var fileLink = document.createElement("a");
          fileLink.href = fileURL;
          fileLink.setAttribute("download", "file.zip");
          document.body.appendChild(fileLink);
          fileLink.click();
        })
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
        });
    },
    async saveResults(allData) {
      this.resultsLoading = true;
      this.dialog = false;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getResults",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
          allData: allData,
        },
        method: "GET",
        responseType: "blob",
        headers: headersList,
      };

      // await axios.request(reqOptions).then(response => (this.message = response.data))
      // // this.snackbar=true

      // reqOptions = {
      //   url: this.url + "getResults",
      //   params: {model_name: this.model.modelNameSelected},
      //   method: "GET",
      //   responseType: 'blob',
      //   headers: headersList,
      //   }

      await axios
        .request(reqOptions)
        .then((response) => {
          var fileURL = window.URL.createObjectURL(new Blob([response.data]));
          var fileLink = document.createElement("a");
          fileLink.href = fileURL;
          fileLink.setAttribute(
            "download",
            this.model.modelNameSelected + ".zip"
          );
          document.body.appendChild(fileLink);
          fileLink.click();
        })
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
        });

      this.resultsLoading = false;
    },
    async getPlot(Variable) {
      this.dialogGetPlot = false;
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };
      let OutputName = "";
      for (var i = 0; i < this.computes.length; i++) {
        if (
          (this.computes[i]["variable"] == "External_Force") |
          this.computes[i]["variable"]
        ) {
          OutputName = this.computes[i]["name"];
          break;
        }
      }
      if (OutputName == "") {
        this.message =
          "No Output was defined with External_Force or External_Displacement";
        this.snackbar = true;
        this.modelLoading = false;
        return;
      }

      let reqOptions = {
        url: this.url + "getPlot",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
          OutputName: OutputName,
        },
        method: "GET",
        headers: headersList,
      };

      this.modelLoading = true;
      await axios
        .request(reqOptions)
        .then((response) => (this.plotRawData = response.data))
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });

      if (Variable == "Time") {
        this.plotData[0].x = this.plotRawData[0].split(",");
        this.plotData[1].x = this.plotRawData[0].split(",");
      } else if (Variable == "Displacement") {
        this.plotData[0].x = this.plotRawData[1].split(",");
        this.plotData[1].x = this.plotRawData[1].split(",");
      }
      this.plotData[0].y = this.plotRawData[1].split(",");
      this.plotData[1].y = this.plotRawData[2].split(",");
      this.viewId = 2;
      this.modelLoading = false;
    },
    async getImage() {
      this.dialogGetImage = false;

      await this.getPointDataAndUpdateDx();

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      console.log(this.$refs.modelView.$el.clientWidth);
      console.log(this.$refs.modelView.$el.clientHeight);

      let reqOptions = {
        url: this.url + "getImage",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
          Output: this.getImageOutput,
          Variable: this.getImageVariableSelected,
          Axis: this.getImageAxisSelected,
          dx_value: this.dx_value,
          width: this.$refs.modelView.$el.clientWidth,
          height: this.$refs.modelView.$el.clientHeight,
        },
        method: "GET",
        responseType: "blob",
        headers: headersList,
      };

      this.modelLoading = true;
      await axios
        .request(reqOptions)
        .then(
          (response) =>
            (this.modelImg = window.URL.createObjectURL(
              new Blob([response.data])
            ))
        )
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });
      this.viewId = 0;
      this.modelLoading = false;
    },
    async getImagePython() {
      this.dialogGetImagePython = false;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getImagePython",
        params: {
          model_name: this.model.modelNameSelected,
          cluster: this.job.cluster,
          output: this.getImageOutput,
          variable: this.getImageVariableSelected,
          axis: this.getImageAxisSelected,
          displ_factor: this.getImageDisplFactor,
          marker_size: this.getImageMarkerSize,
          length: this.model.length,
          height: this.model.height,
        },
        method: "GET",
        responseType: "blob",
        headers: headersList,
      };

      this.modelLoading = true;
      await axios
        .request(reqOptions)
        .then(
          (response) =>
            (this.modelImg = window.URL.createObjectURL(
              new Blob([response.data])
            ))
        )
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });
      this.viewId = 0;
      this.modelLoading = false;
    },
    async getG1c() {
      this.dialogGetG1c = false;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getG1c",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
          Output: this.getG1cOutput,
          Frequency: this.getG1cFrequency,
        },
        method: "GET",
        responseType: "application/json",
        headers: headersList,
      };

      this.modelLoading = true;
      await axios
        .request(reqOptions)
        .then((response) => (this.plotRawData = response.data))
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });
      console.log(this.plotRawData);
      this.plotData[0].x = this.plotRawData[2];
      this.plotData[0].name = "Crack length";
      this.plotData[0].y = this.plotRawData[1];

      this.viewId = 2;
      this.modelLoading = false;
    },
    async getG2c() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "calculateG2c",
        params: {
          model_name: this.model.modelNameSelected,
          cluster: this.job.cluster,
          output: this.getG1cOutput,
        },
        data: this.model,
        method: "POST",
        responseType: "application/json",
        headers: headersList,
      };

      this.modelLoading = true;
      var giic = 0;
      await axios
        .request(reqOptions)
        .then((response) => (giic = response.data))
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });
      console.log(giic);
      this.message = "GIIC = " + giic;
      this.snackbar = true;

      this.modelLoading = false;
    },
    openCara() {
      window.open("https://cara.dlr.de/enginframe/vdi/vdi.xml", "_blank");
    },
    openResults() {
      window.open(this.resultPort, "_blank");
    },
    async showResults(outputName) {
      this.dialogShowResults = false;
      this.modelLoading = true;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      var index = this.outputs.findIndex((o) => o.name == outputName);

      let output_list = [];

      if (this.outputs[index].Displacement) {
        output_list.push("Displacement");
      }
      if (this.outputs[index].Force) {
        output_list.push("Force");
      }
      if (this.outputs[index].Velocity) {
        output_list.push("Velocity");
      }
      if (this.outputs[index].Damage) {
        output_list.push("Damage");
      }
      if (this.outputs[index].Partial_Stress) {
        output_list.push("Partial_StressX");
        output_list.push("Partial_StressY");
        output_list.push("Partial_StressZ");
      }
      if (this.outputs[index].Number_Of_Neighbors) {
        output_list.push("Number_Of_Neighbors");
      }

      let reqOptions = {
        url: this.trameUrl + "launchTrameInstance",
        params: {
          model_name: this.model.modelNameSelected,
          output_name: this.outputs[index].name,
          output_list: output_list.toString(),
          dx_value: this.dx_value,
          duration: 600,
        },
        method: "POST",
        headers: headersList,
      };

      console.log(reqOptions);
      await axios
        .request(reqOptions)
        .then((response) => (this.port = response.data))
        .catch((error) => {
          this.message = error;
          this.snackbar = true;
          this.modelLoading = false;
          return;
        });

      if (process.env.VUE_APP_DEV) {
        this.resultPort =
          this.trameUrl.slice(0, this.trameUrl.length - 5) + this.port;
      } else {
        switch (this.port) {
          case 6041:
            this.resultPort =
              "http://perihub-trame-gui1.fa-services.intra.dlr.de:443";
            break;
          case 6042:
            this.resultPort =
              "http://perihub-trame-gui2.fa-services.intra.dlr.de:443";
            break;
          case 6043:
            this.resultPort =
              "http://perihub-trame-gui3.fa-services.intra.dlr.de:443";
            break;
          case 6044:
            this.resultPort =
              "http://perihub-trame-gui4.fa-services.intra.dlr.de:443";
            break;
          case 6045:
            this.resultPort =
              "http://perihub-trame-gui5.fa-services.intra.dlr.de:443";
            break;
        }
      }

      await sleep(17000);
      this.modelLoading = false;

      this.viewId = 3;
      document.querySelectorAll("iframe").forEach(function (e) {
        e.src += "";
      });
    },
    monitorLogFile() {
      if (this.monitorToggle) {
        this.getLogFile();
        this.logInterval = setInterval(() => {
          this.getLogFile();
        }, 30000);
      } else {
        clearInterval(this.logInterval);
      }
    },
    monitorStatus(setClear) {
      this.getStatus();
      if (setClear) {
        this.statusInterval = setInterval(() => {
          this.getStatus();
        }, 30000);
      } else {
        clearInterval(this.statusInterval);
      }
    },
    async getLogFile() {
      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "getLogFile",
        params: {
          model_name: this.model.modelNameSelected,
          cluster: this.job.cluster,
        },
        method: "GET",
        headers: headersList,
      };

      this.textLoading = true;
      await axios
        .request(reqOptions)
        .then((response) => (this.textOutput = response.data));
      this.textLoading = false;

      this.getStatus();
    },
    writeInputFile() {
      let reqOptions = {
        url: this.url + "writeInputFile",
        params: {
          model_name: this.model.modelNameSelected,
          input_string: this.textOutput,
          file_type: this.solver.filetype,
        },
        method: "PUT",
      };

      axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));
    },
    async deleteModel() {
      this.dialogDeleteModel = false;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "deleteModel",
        params: { model_name: this.model.modelNameSelected },
        method: "DELETE",
        headers: headersList,
      };

      axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));

      reqOptions = {
        url: this.url + "deleteModelFromCluster",
        params: {
          model_name: this.model.modelNameSelected,
          Cluster: this.job.cluster,
        },
        method: "DELETE",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));
      this.snackbar = true;
      this.getStatus();
    },
    async deleteUserData() {
      this.dialogDeleteUserData = false;

      let headersList = {
        "Cache-Control": "no-cache",
        Authorization: this.authToken,
      };

      let reqOptions = {
        url: this.url + "deleteUserData",
        params: { checkDate: false },
        method: "DELETE",
        headers: headersList,
      };

      axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));
      reqOptions = {
        url: this.url + "deleteUserDataFromCluster",
        params: { Cluster: this.job.cluster, checkDate: false },
        method: "DELETE",
        headers: headersList,
      };

      await axios
        .request(reqOptions)
        .then((response) => (this.message = response.data));
      this.snackbar = true;
      this.getStatus();
    },
    addMaterial() {
      const len = this.materials.length;
      this.materials.push({
        materialsId: len + 1,
        name: "Material" + (len + 1),
      });
      for (const key in this.materials[len - 1]) {
        if ((key != "materialsId") & (key != "name")) {
          this.$set(this.materials[len], key, this.materials[len - 1][key]);
        }
      }
    },
    removeMaterial(index) {
      this.materials.splice(index, 1);
    },
    addProp(index) {
      const len = this.materials[index].properties.length;
      this.materials[index].properties.push({
        materialsPropId: len + 1,
        name: "Prop_" + (len + 1),
      });
      for (const key in this.materials[index].properties[len - 1]) {
        if ((key != "materialsPropId") & (key != "name")) {
          this.$set(
            this.materials[index].properties[len],
            key,
            this.materials[index].properties[len - 1][key]
          );
        }
      }
    },
    removeProp(index, subindex) {
      this.materials[index].properties.splice(subindex, 1);
    },
    addDamage() {
      const len = this.damages.length;
      this.damages.push({
        damagesId: len + 1,
        name: "Damage" + (len + 1),
      });
      for (const key in this.damages[len - 1]) {
        if ((key != "damagesId") & (key != "name")) {
          this.$set(this.damages[len], key, this.damages[len - 1][key]);
        }
      }
    },
    removeDamage(index) {
      this.damages.splice(index, 1);
      if (this.damages.length == 0) {
        for (var i = 0; i < this.blocks.length; i++) {
          this.blocks[i].damageModel = "";
        }
      }
    },
    addInterBlock(index) {
      const len = this.damages[index].interBlocks.length;
      this.damages[index].interBlocks.push({
        damagesInterId: len + 1,
        firtsId: 1,
        secondId: len + 1,
      });
      for (const key in this.damages[index].interBlocks[len - 1]) {
        if (key == "value") {
          this.$set(
            this.damages[index].interBlocks[len],
            key,
            this.damages[index].interBlocks[len - 1][key]
          );
        }
      }
    },
    removeInterBlock(index, subindex) {
      this.damages[index].interBlocks.splice(subindex, 1);
    },
    addBlock() {
      const len = this.blocks.length;
      this.blocks.push({
        blocksId: len + 1,
        name: "block_" + (len + 1),
      });
      for (const key in this.blocks[len - 1]) {
        if ((key != "blocksId") & (key != "name")) {
          this.$set(this.blocks[len], key, this.blocks[len - 1][key]);
        }
      }
    },
    removeBlock(index) {
      this.blocks.splice(index, 1);
    },
    addCondition() {
      const len = this.boundaryConditions.length;
      this.boundaryConditions.push({
        boundaryConditionsId: len + 1,
        name: "BC_" + (len + 1),
      });
      for (const key in this.boundaryConditions[len - 1]) {
        if ((key != "boundaryConditionsId") & (key != "name")) {
          this.$set(
            this.boundaryConditions[len],
            key,
            this.boundaryConditions[len - 1][key]
          );
        }
      }
    },
    removeCondition(index) {
      this.boundaryConditions.splice(index, 1);
    },
    addBondFilter() {
      const len = this.bondFilters.length;
      this.bondFilterPoints.push({
        bondFilterPointsId: len + 1,
        bondFilterPointString: [],
      });
      this.bondFilters.push({
        bondFilterId: len + 1,
        name: "bf_" + (len + 1),
      });
      for (const key in this.bondFilters[len - 1]) {
        if ((key != "bondFilterId") & (key != "name")) {
          this.$set(this.bondFilters[len], key, this.bondFilters[len - 1][key]);
        }
      }
    },
    removeBondFilter(index) {
      this.bondFilters.splice(index, 1);
      this.bondFilterPoints.splice(index, 1);
    },
    addContactModel() {
      const len = this.contact.contactModels.length;
      this.contact.contactModels.push({
        contactModelsId: len + 1,
        name: "Contact Model " + (len + 1),
      });
      for (const key in this.contact.contactModels[len - 1]) {
        if ((key != "contactModelsId") & (key != "name")) {
          this.$set(
            this.contact.contactModels[len],
            key,
            this.contact.contactModels[len - 1][key]
          );
        }
      }
    },
    removeContactModel(index) {
      this.contact.contactModels.splice(index, 1);
    },
    addInteraction() {
      const len = this.contact.interactions.length;
      this.contact.interactions.push({
        contactInteractionsId: len + 1,
      });
      for (const key in this.contact.interactions[len - 1]) {
        if (key != "contactInteractionsId") {
          this.$set(
            this.contact.interactions[len],
            key,
            this.contact.interactions[len - 1][key]
          );
        }
      }
    },
    removeInteraction(index) {
      this.contact.interactions.splice(index, 1);
    },
    addCompute() {
      const len = this.computes.length;
      this.computes.push({
        computesId: len + 1,
        name: "Compute" + (len + 1),
      });
      for (const key in this.computes[len - 1]) {
        if ((key != "computesId") & (key != "name")) {
          this.$set(this.computes[len], key, this.computes[len - 1][key]);
        }
      }
    },
    removeCompute(index) {
      this.computes.splice(index, 1);
    },
    addOutput() {
      const len = this.outputs.length;
      this.outputs.push({
        outputsId: len + 1,
        name: "Output" + (len + 1),
        Displacement: false,
        Force: false,
        Damage: false,
        Partial_Stress: false,
        Number_Of_Neighbors: false,
        Contact_Force: false,
        Horizon: false,
        Model_Coordinates: false,
        Local_Angles: false,
        Coordinates: false,
        Acceleration: false,
        Temperature: false,
        Temperature_Change: false,
        Force_Density: false,
        External_Force_Density: false,
        Damage_Model_Data: false,
        Velocity_Gradient: false,
        PiolaStressTimesInvShapeTensor: false,
        Write_After_Damage: false,
        InitStep: 0,
      });
    },
    removeOutput(index) {
      this.outputs.splice(index, 1);
    },
    modelNameChangedEvent() {
      this.showModelImg();
      this.getStatus();
      this.resetData();
    },
    showModelImg() {
      switch (this.model.modelNameSelected) {
        case "GICmodel":
          this.modelImg = GICmodelImage;
          break;
        case "GIICmodel":
          this.modelImg = GIICmodelImage;
          break;
        case "DCBmodel":
          this.modelImg = DCBmodelImage;
          break;
        case "Dogbone":
          this.modelImg = DogboneImage;
          break;
        case "Kalthoff-Winkler":
          this.modelImg = KalthoffWinklerImage;
          break;
        case "PlateWithHole":
          this.modelImg = PlateWithHoleImage;
          break;
        case "CompactTension":
          this.modelImg = CompactTensionImage;
          break;
      }
      this.viewId = 0;
    },
    changeToXml() {
      if (this.job.cluster == "FA-Cluster") {
        this.solver.filetype = "xml";
      } else {
        this.solver.filetype = "yaml";
      }
    },
    changeNumberOfTasks() {
      if (this.job.cluster == "FA-Cluster") {
        if (this.job.tasks > 32) {
          this.job.tasks = 32;
        }
      } else if (this.job.cluster == "None") {
        this.job.tasks = 1;
      }
    },
    checkInputs() {
      if (this.model.length) {
        return true;
      }

      this.errors = [];

      if (!this.model.length) {
        this.errors.push("Length required");
      }
      // if (!this.model.width) {
      //   this.errors.push('Width required');
      // }

      this.message = this.errors.join("\n");

      this.snackbar = true;

      return false;
    },
    getCurrentData() {
      this.getLocalStorage("model");
      this.getLocalStorage("materials");
      this.getLocalStorage("damages");
      this.getLocalStorage("blocks");
      this.getLocalStorage("contact");
      this.getLocalStorage("boundaryConditions");
      this.getLocalStorage("bondFilters");
      this.getLocalStorage("computes");
      this.getLocalStorage("outputs");
      this.getLocalStorage("solver");
      this.getLocalStorage("job");
      this.getLocalStorage("panel");
    },
    getLocalStorage(name) {
      if (localStorage.getItem(name))
        var object = JSON.parse(localStorage.getItem(name));
      if (object != undefined) {
        if (Object.keys(object).length != 0) {
          if (Array.isArray(object)) {
            this[name] = [...JSON.parse(localStorage.getItem(name))];
          } else {
            this[name] = { ...JSON.parse(localStorage.getItem(name)) };
          }
        }
      }
    },
    deleteCookies() {
      this.dialogDeleteCookies = false;
      this.$cookie.delete("darkMode");
      localStorage.removeItem("model");
      localStorage.removeItem("materials");
      localStorage.removeItem("damages");
      localStorage.removeItem("blocks");
      localStorage.removeItem("contact");
      localStorage.removeItem("boundaryConditions");
      localStorage.removeItem("bondFilters");
      localStorage.removeItem("computes");
      localStorage.removeItem("outputs");
      localStorage.removeItem("solver");
      localStorage.removeItem("job");
      localStorage.removeItem("panel");
    },
    getAuthToken() {
      let reqOptions = {
        url: "https://perihub.fa-services.intra.dlr.de",
      };
      axios
        .request(reqOptions)
        .then((response) => (this.authToken = response.headers.authorization));
      // console.log(this.authToken);
    },
    openHidePanels() {
      if (this.panel.length == 0) {
        this.panel = [0, 1, 2, 3, 4, 5, 6, 7];
      } else {
        this.panel = [];
      }
    },
    openErrorDialog(message) {
      this.errorMessage = message;
      this.dialogError = true;
    },
    showTutorial() {
      var color = "gray";
      if (this.$cookie.get("darkMode") == "true") {
        color = "gray";
      } else {
        color = "white";
      }
      console.log(this.$cookie.get("darkMode"));
      console.log(color);

      const driver = new Driver({
        animate: true, // Animate while changing highlighted element
        opacity: 0.5,
        stageBackground: color,
      });

      // Define the steps for introduction
      driver.defineSteps([
        {
          element: "#model-configuration",
          popover: {
            className: "first-step-popover-class",
            title: "Title on Popover",
            description: "Body of the popover",
            position: "right",
          },
        },
        {
          element: "#model-output",
          popover: {
            title: "Title on Popover",
            description: "Body of the popover",
            position: "left",
          },
        },
        {
          element: "#button-runModel",
          popover: {
            title: "Title on Popover",
            description: "Body of the popover",
            position: "bottom",
          },
        },
      ]);

      // Start the introduction
      driver.start();
    },
  },
  beforeMount() {
    // console.log("beforeMount")
    if (process.env.VUE_APP_DEV != undefined) {
      if (process.env.VUE_APP_DEV) {
        console.log("--- Running in development mode ---");
        this.url = "http://localhost:6020/";
        console.log("changed URL: " + this.url);
        this.trameUrl = "http://localhost:6040/";
        console.log("changed Trame URL: " + this.trameUrl);
      }
    } else {
      this.getAuthToken();
    }
  },
  mounted() {
    // console.log("mounted")
    this.getCurrentData();
    this.getStatus();
    this.showModelImg();
  },
  updated() {
    // console.log("updated")
    // console.log(this.model.modelNameSelected)
    // console.log(this.$store.state.modelName)
    // this.saveCurrentData()
    // console.log(this.model.modelNameSelected)
    // console.log(this.$store.state.modelName)
  },
  beforeUnmount() {
    // console.log("beforeUnmount")
    // Don't forget to remove the interval before destroying the component
    clearInterval(this.logInterval);
    clearInterval(this.statusInterval);

    if (port != "") {
      let reqOptions = {
        url: this.trameUrl + "closeTrameInstance",
        params: {
          port: this.port,
          cron: false,
        },
        method: "POST",
        headers: headersList,
      };

      axios.request(reqOptions);
    }
  },
  watch: {
    model: {
      handler() {
        console.log("model changed!");
        localStorage.setItem("model", JSON.stringify(this.model));
      },
      deep: true,
    },
    materials: {
      handler() {
        console.log("materials changed!");
        localStorage.setItem("materials", JSON.stringify(this.materials));
      },
      deep: true,
    },
    damages: {
      handler() {
        // console.log('damages changed!');
        localStorage.setItem("damages", JSON.stringify(this.damages));
      },
      deep: true,
    },
    blocks: {
      handler() {
        // console.log('blocks changed!');
        localStorage.setItem("blocks", JSON.stringify(this.blocks));
      },
      deep: true,
    },
    contact: {
      handler() {
        // console.log('contact changed!');
        localStorage.setItem("contact", JSON.stringify(this.contact));
      },
      deep: true,
    },
    boundaryConditions: {
      handler() {
        // console.log('boundaryConditions changed!');
        localStorage.setItem(
          "boundaryConditions",
          JSON.stringify(this.boundaryConditions)
        );
      },
      deep: true,
    },
    bondFilters: {
      handler() {
        console.log("bondFilters changed!");
        this.showHideBondFilters();
        localStorage.setItem("bondFilters", JSON.stringify(this.bondFilters));
      },
      deep: true,
    },
    computes: {
      handler() {
        // console.log('computes changed!');
        localStorage.setItem("computes", JSON.stringify(this.computes));
      },
      deep: true,
    },
    outputs: {
      handler() {
        // console.log('outputs changed!');
        localStorage.setItem("outputs", JSON.stringify(this.outputs));
      },
      deep: true,
    },
    solver: {
      handler() {
        // console.log('solver changed!');
        localStorage.setItem("solver", JSON.stringify(this.solver));
      },
      deep: true,
    },
    job: {
      handler() {
        // console.log('job changed!');
        localStorage.setItem("job", JSON.stringify(this.job));
      },
      deep: true,
    },
    panel: {
      handler() {
        // console.log('panel changed!');
        localStorage.setItem("panel", JSON.stringify(this.panel));
      },
      deep: true,
    },
  },
};
