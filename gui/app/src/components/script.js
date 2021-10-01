
 import axios from 'axios'
//  import vueJsonEditor from 'vue-json-editor'
//  import VueJsonPretty from 'vue-json-pretty'
//  import 'vue-json-pretty/lib/styles.css'
import { PrismEditor } from "vue-prism-editor";
import "vue-prism-editor/dist/prismeditor.min.css"; // import the styles somewhere

// import highlighting library (you can use any library you want just return html string)
import { highlight, languages } from "prismjs/components/prism-core";
import "prismjs/components/prism-clike";
import "prismjs/components/prism-javascript";
import "prismjs/themes/prism-tomorrow.css"; // import syntax highlighting styles

import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
// import pdf from 'vue-pdf'
// import { colormap } from 'colormap';
// import RemoteComponent from "vue-remote-component";
import GIICmodelImage from '../assets/GIICmodel/GIICmodel.jpg'
import GIICmodelFile from '../assets/GIICmodel/GIICmodel.json'
import DCBmodelImage from '../assets/DCBmodel/DCBmodel.jpg'
import DCBmodelFile from '../assets/DCBmodel/DCBmodel.json'
import DogboneImage from '../assets/Dogbone/Dogbone.jpg'
import DogboneFile from '../assets/Dogbone/Dogbone.json'
import { Plotly } from 'vue-plotly'

  export default {
    name: 'ModelGenerator',
    components: {
      PrismEditor,
      Splitpanes,
      Pane,
      Plotly,
      // pdf
      // RemoteComponent
    },
    data () {
      return {
        // Model
        modelName: ['Dogbone', 'GIICmodel', 'DCBmodel'],
        modelNameSelected: 'GIICmodel',
        length: 50,
        width: 10,
        height: 4.95,
        height2: 4.95,
        discretization: 11,
        twoDimensional: true,
        rotatedAngles: true,
        angles: [0, 0],
        // Material
        materialModelName: ['Elastic', 'Multiphysics Elastic', 'Elastic Plastic', 'Elastic Plastic Hardening', 'Viscoelastic', 'Elastic Plastic Correspondence', 'Elastic Correspondence', 'Viscoplastic Needleman Correspondence', 'Isotropic Hardening Correspondence', 'Elastic Hypoelastic Correspondence', 'Elastic Plastic Hypoelastic Correspondence', 'Isotropic Hardening Hypoelastic Correspondence', 'LCM', 'Elastic Bond Based', 'Vector Poisson', 'Diffusion', 'Pals', 'Linear LPS Partial Volume', 'Linear Elastic Correspondence', 'Elastic Partial Volume', 'Elastic Correspondence Partial Stress', 'Pressure Dependent Elastic Plastic'],
        materialSymmetry: ['Isotropic', 'Anisotropic'],
        stabilizatonType: ['Bond Based', 'State Based', 'Sub Horizon', 'Global Stiffness'],
        materials: [
          { id: 1, Name: 'PMMA', 
            MatType: 'Linear Elastic Correspondence', 
            bulkModulus: 630000.0,
            youngsModulus: 210000.0,
            poissonsRatio: 0.3,
            tensionSeparation: false,
            planeStress: true,
            materialSymmetry: 'Anisotropic',
            stabilizatonType: 'Global Stiffness',
            thickness: 10.0,
            hourglassCoefficient: 1.0,
            actualHorizon: '',
            yieldStress: '',
            Parameter: {
              Density: {'value': 1.95e-07}, 
              C11: {'value': 165863.6296530634},
              C12: {'value': 4090.899504376252},
              C13: {'value': 2471.126276093059},
              C14: {'value': 0.0},              
              C15: {'value': 0.0},              
              C16: {'value': 0.0},              
              C22: {'value': 9217.158022124806},
              C23: {'value': 2471.126276093059},
              C24: {'value': 0.0},              
              C25: {'value': 0.0},              
              C26: {'value': 0.0},              
              C33: {'value': 9217.158022124804},
              C34: {'value': 0.0},              
              C35: {'value': 0.0},              
              C36: {'value': 0.0},              
              C44: {'value': 3360.0},           
              C45: {'value': 0.0},              
              C46: {'value': 0.0},              
              C55: {'value': 4200.0},           
              C56: {'value': 0.0},              
              C66: {'value': 4200.0}}}],
        nextMaterialId: 2,
        // Damage
        damageModelName: ['Critical Stretch', 'Interface Aware', 'Time Dependent Critical Stretch', 'Critical Energy', 'Initial Damage', 'Time Dependent Critical Stretch', 'Critical Energy Correspondence'],
        damages: [
          { id: 1, Name: 'PMMADamage', 
            damageModel: 'Critical Energy Correspondence',
            criticalStretch: 10,
            criticalEnergy: 5.1,
            interblockdamageEnergy: 0.01,
            planeStress: true,
            onlyTension: true,
            detachedNodesCheck: true,
            thickness: 10.0,
            hourglassCoefficient: 1.0,
            stabilizatonType: 'Global Stiffness'}],
        nextdamageId: 2,
        // Blocks 
        blocks: [
          { id: 1, Name: 'block_1', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 2, Name: 'block_2', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 3, Name: 'block_3', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 4, Name: 'block_4', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 5, Name: 'block_5', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 6, Name: 'block_6', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 7, Name: 'block_7', material: 'PMMA', damageModel: '', interface: '', show: true},
          { id: 8, Name: 'block_8', material: 'PMMA', damageModel: 'PMMADamage', interface: 9, show: true},
          { id: 9, Name: 'block_9', material: 'PMMA', damageModel: 'PMMADamage', interface: 8, show: true},
          { id: 10, Name: 'block_10', material: 'PMMA', damageModel: '', interface: '', show: true},
          ],
        nextBlockId: 11,
        //  boundaryConditions
        boundarytype: ['Initial Displacement', 'Initial Velocity', 'Prescribed Displacement', 'Prescribed Fluid Pressure U', 'Initial Fluid Pressure U', 'Initial Temperature', 'Prescribed Temperature', 'Thermal Flux', 'Body Force'],
        coordinate: ['x', 'y', 'z'],
        boundaryConditions: [
          { id: 1, Name: 'BC_1', boundarytype: 'Prescribed Displacement',  blockId: 5, coordinate: 'y', value: '0*t'},
          { id: 2, Name: 'BC_2', boundarytype: 'Prescribed Displacement',  blockId: 6, coordinate: 'y', value: '0*t'},
          { id: 3, Name: 'BC_3', boundarytype: 'Prescribed Displacement',  blockId: 7, coordinate: 'y', value: '-10*t'},
          { id: 4, Name: 'BC_4', boundarytype: 'Prescribed Displacement',  blockId: 10, coordinate: 'y', value: '0*t'},
          ],
        nextBoundaryConditionId: 4,
        // Compute 
        calculationType: ['Sum', 'Maximum', 'Minimum'],
        variables: ['Force', 'Displacement', 'Damage'],
        computes: [
          { id: 1, Name: 'External_Displacement', variable: 'Displacement', calculationType: 'Minimum', blockName: 'block_7'},
          { id: 2, Name: 'External_Force', variable: 'Force', calculationType: 'Sum', blockName: 'block_7'}],
        nextComputeId: 3,
        // Output 
        outputs: [
          { id: 1, Name: 'Output1', Displacement: true, Force: true, Damage: true, Partial_Stress: true, External_Force: false, External_Displacement: false, Number_Of_Neighbors: false, Frequency: 4000, InitStep: 0},
          { id: 2, Name: 'Output2', Displacement: false, Force: false, Damage: true, Partial_Stress: false, External_Force: true, External_Displacement: true, Number_Of_Neighbors: false, Frequency: 200, InitStep: 0}],
        nextOutputId: 3,
        // Solver
        solver: {
          verbose: false,
          initialTime: 0.0,
          finalTime: 0.03,
          solvertype: 'Verlet',
          safetyFactor: 0.95,
          numericalDamping: 0.000005,
          peridgimPreconditioner: 'None',
          nonlinearSolver: 'Line Search Based',
          numberofLoadSteps: 100,
          maxSolverIterations: 50,
          relativeTolerance: 0.00000001,
          maxAgeOfPrec: 100,
          directionMethod: 'Newton',
          newton: {jacobianOperator: 'Matrix-Free', preconditioner: 'None'},
          lineSearchMethod: 'Polynomial',
          verletSwitch: true,
          verlet: {safetyFactor: 0.95, numericalDamping: 0.000005, outputFrequency: 7500},
          stopAfterDamageInitation: false,
          stopBeforeDamageInitation: false,
          adaptivetimeStepping: false,
          adapt: {stableStepDifference: 4, maximumBondDifference: 4, stableBondDifference: 1},
          filetype: 'yaml',
        },
        solvertype: ['Verlet', 'NOXQuasiStatic'],
        peridgimPreconditioner: ['Full Tangent', 'Block 3x3', 'None'],
        nonlinearSolver: ['Line Search Based'],
        directionMethod: ['Newton', 'NonlinearCG'],
        jacobianOperator: ['Matrix-Free', ''],
        preconditioner: ['User Defined', 'None'],
        lineSearchMethod: ['Polynomial'],
        filetype: ['yaml', 'xml'],
        // Job
        job: {
          cluster: 'Cara',
          tasks: 1280,
          time: '40:00:00',
          // user: 'hess_ja',
          account: '2263032',
          // mail: 'jan-timo.hesse@dlr.de',
        },
        cluster: ['Cara', 'FA-Cluster', 'None'],


        yamlOutput: '',
        pointString: [1,0,0],
        filteredPointString: [1,0,0],
        blockIdString: [1],
        filteredBlockIdString: [1],
        resolution: 6,
        radius: 0.2,
        multiplier: 1,
        snackbar: false,
        message: 'Messsages',
        loading: false,
        resultsLoading: false,
        dataJson: '',
        colors: '',
        modelImg: GIICmodelImage,
        jsonFIle: GIICmodelFile,
        dialog: false,
        dialogDeleteModel: false,
        dialogDeleteUserData: false,
        errors: [],
        plot:[{
        x: [1,2,3,4],
        y: [10,15,13,17],
        type:"scatter"
        }],
        layout:{
          title: "My graph"
        },
        viewId: 0,
        rules: {
          required: value => !!value || value == 0 || 'Required',
          name: value => {
            const pattern = /^[A-Za-z0-9_]{1,15}/
            return pattern.test(value) || 'Invalid name'
          },
          float: value => {
            const pattern = /^((?!0)|[-]|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/
            return pattern.test(value) || 'Invalid number'
          },
          int: value => {
            const pattern = /^[-]{0,1}(?<!\.)\d+(?!\.)$/
            return pattern.test(value) || 'Invalid number'
          },
        },
      }
    },
    filters: {
      number(value)
      {
        return value.toFixed(2)
      }
    },
    methods: {

      highlighter(code) {
        return highlight(code, languages.js); // languages.<insert language> to return html with markup
      },

      viewInputFile() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/viewInputFile",
          params: {ModelName: this.modelNameSelected,
                  FileType: this.solver.filetype},
          method: "GET",
          headers: headersList,
          }

        axios.request(reqOptions).then(response => (this.yamlOutput = response.data))
      },
      async generateModel() {
        // this.snackbar=true
        // this.message = JSON.parse("{\"Param\":" + "{\"Material\": " + JSON.stringify(this.materials)+",\n" +
        //                                     "\"Solver\": " + JSON.stringify(this.solver)+",\n" +
        //                                     "\"Output\": " + JSON.stringify(this.outputs) + "}}")
        if(this.checkInputs()){
          let headersList = {
          'Cache-Control': 'no-cache'
          }

          let reqOptions = {
            url: "http://localhost:8000/generateModel",
            params: {ModelName: this.modelNameSelected,
                    Length: this.length,
                    Width: this.width,
                    Height: this.height,
                    Height2: this.height2,
                    Discretization: this.discretization,
                    TwoDimensional: this.twoDimensional,
                    RotatedAngles: this.rotatedAngles,
                    Angle0: this.angles[0],
                    Angle1: this.angles[1],
                    Solvertype: this.solvertypeSelected,},
            data: JSON.parse("{\"Param\":" + "{\"Material\": " + JSON.stringify(this.materials)+",\n" +
                                              "\"Damage\": " + JSON.stringify(this.damages)+",\n" +
                                              "\"Block\": " + JSON.stringify(this.blocks)+",\n" +
                                              "\"BoundaryConditions\": " + JSON.stringify(this.boundaryConditions)+",\n" +
                                              "\"Compute\": " + JSON.stringify(this.computes)+",\n" +
                                              "\"Output\": " + JSON.stringify(this.outputs)+",\n" +
                                              "\"Solver\": " + JSON.stringify(this.solver) + "}}"),
            method: "POST",
            headers: headersList,
          }
          this.loading = true
          await axios.request(reqOptions).then(response => (this.message = response.data))
          this.snackbar=true
          this.viewInputFile()
          this.viewPointData()
          this.loading = false
        }
      },
      saveData() {
        const data = "{\"modelNameSelected\":\"" + this.modelNameSelected + "\",\n" +
                      "\"length\":" + this.length + ",\n" +
                      "\"width\":" + this.width + ",\n" +
                      "\"height\":" + this.height + ",\n" +
                      "\"height2\":" + this.height2 + ",\n" +
                      "\"discretization\":" + this.discretization + ",\n" +
                      "\"twoDimensional\":" + this.twoDimensional + ",\n" +
                      "\"rotatedAngles\":" + this.rotatedAngles + ",\n" +
                      "\"angles\":[" + this.angles + "],\n" +
                      "\"Param\":" + "{\"materials\": " + JSON.stringify(this.materials)+",\n" +
                                      "\"damages\": " + JSON.stringify(this.damages)+",\n" +
                                      "\"blocks\": " + JSON.stringify(this.blocks)+",\n" +
                                      "\"boundaryConditions\": " + JSON.stringify(this.boundaryConditions)+",\n" +
                                      "\"computes\": " + JSON.stringify(this.computes)+",\n" +
                                      "\"outputs\": " + JSON.stringify(this.outputs)+",\n" +
                                      "\"solver\": " + JSON.stringify(this.solver) + "}}";
        var fileURL = window.URL.createObjectURL(new Blob([data], {type: 'application/json'}));
        var fileLink = document.createElement('a');
        fileLink.href = fileURL;
        fileLink.setAttribute('download', this.modelNameSelected + '.json');
        document.body.appendChild(fileLink);
        fileLink.click();
      },
      readData() {
        this.$refs.fileInput.click()
      },
      onFilePicked (event) {
        const files = event.target.files
        if (files.length <= 0) {
          return false;
        }

        const fr = new FileReader();

        fr.onload = e => {
          const result = JSON.parse(e.target.result);
          for(var i = 0; i < Object.keys(result).length; i++) {
            var name = Object.keys(result)[i]
            if (name!='Param'){
              this[name] = result[name];
            }
            else{
              // var param = result[i]
              for(var j = 0; j < Object.keys(result['Param']).length; j++) {
                var paramName = Object.keys(result['Param'])[j]
                this[paramName] = result['Param'][paramName];
              }
            }
          }
        }
        fr.readAsText(files.item(0));
      },
      resetData() {
        switch (this.modelNameSelected) {
        case 'GIICmodel':  
          this.jsonFile = GIICmodelFile;
          break;
        case 'DCBmodel':  
          this.jsonFile = DCBmodelFile;
          break;
        case 'Dogbone':  
          this.jsonFile = DogboneFile;
          break;
        }

        for(var i = 0; i < Object.keys(this.jsonFile).length; i++) {
          var name = Object.keys(this.jsonFile)[i]
          if (name!='Param'){
            this[name] = this.jsonFile[name];
          }
          else{
            // var param = result[i]
            for(var j = 0; j < Object.keys(this.jsonFile['Param']).length; j++) {
              var paramName = Object.keys(this.jsonFile['Param'])[j]
              this[paramName] = this.jsonFile['Param'][paramName];
            }
          }
        }
      },
      async viewPointData() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/getPointData",
          params: {ModelName: this.modelNameSelected},
          method: "GET",
          headers: headersList,
          }

        this.loading = true
        await axios.request(reqOptions).then(response => (
          this.pointString = response.data[0].split(','),
          this.blockIdString = response.data[1].split(',')))
        this.filterPointData()
        this.viewId = 1
        this.$refs.view.resetCamera()
        this.loading = false
      },
      filterPointData() {
        this.loading = true
        var idx = 0
        this.filteredBlockIdString = []
        this.filteredPointString = []
        for (var i = 0; i < this.blockIdString.length; i++) {
          if (this.blocks[this.blockIdString[i]*10-1].show){
            this.filteredBlockIdString[idx] = this.blockIdString[i]
            for (var j = 0; j < 3; j++) {
              this.filteredPointString[idx*3+j] = this.pointString[i*3+j] * this.multiplier
            }
            idx +=1 
          }
        }
        this.loading = false
      },
      updatePoints() {
        if (this.radius<=0.2){
          this.multiplier=(1-(this.radius/0.5))*30
          this.filterPointData()
        }
        else{
          this.multiplier=1
          this.filterPointData()
        }
      },
      async copyModelToCluster() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/copyModelToCluster",
          params: {ModelName: this.modelNameSelected,
                  Cluster: this.job.cluster},
          method: "GET",
          headers: headersList,
        }
        this.loading = true
        await axios.request(reqOptions).then(response => (this.message = response.data))
        this.loading = false
        this.snackbar=true
      },
      runModel() {
        // this.snackbar=true
        // this.message = JSON.parse("{\"Job\": " + JSON.stringify(this.job)+"}")
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/runModel",
          params: {ModelName: this.modelNameSelected,
                  FileType: this.solver.filetype,},
          data: JSON.parse("{\"Param\":" + "{\"Job\": " + JSON.stringify(this.job)+",\n" +
                                            "\"Output\": " + JSON.stringify(this.outputs) + "}}"),
          method: "POST",
          headers: headersList,
        }

        axios.request(reqOptions).then(response => (this.message = response.data))
        this.snackbar=true
      },
      cancelJob() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/cancelJob",
          params: {ModelName: this.modelNameSelected,
                  Cluster: this.job.cluster,},
          method: "POST",
          headers: headersList,
        }

        axios.request(reqOptions).then(response => (this.message = response.data))
        this.snackbar=true
      },
      saveModel() {
        let headersList = {
        'Cache-Control': 'no-cache',
        'X-Forwarded-Email': 'jan-timo.hesse@dlr.de',
        'X-Forwarded-Preferred-Username': 'hess_ja'
        }

        let reqOptions = {
          url: "http://localhost:8000/getModel",
          params: {ModelName: this.modelNameSelected},
          method: "GET",
          responseType: 'blob',
          headers: headersList,
          }

        axios.request(reqOptions).then((response) => {
            var fileURL = window.URL.createObjectURL(new Blob([response.data]));
            var fileLink = document.createElement('a');
            fileLink.href = fileURL;
            fileLink.setAttribute('download', 'file.zip');
            document.body.appendChild(fileLink);
            fileLink.click();

        });
      },
      async saveResults(allData) {
        this.resultsLoading = true;
        this.dialog = false;

        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/getResults",
          params: {ModelName: this.modelNameSelected,
                  Cluster: this.job.cluster,
                  allData: allData},
          method: "GET",
          responseType: 'blob',
          headers: headersList,
          }
          
        // await axios.request(reqOptions).then(response => (this.message = response.data))
        // // this.snackbar=true

        // reqOptions = {
        //   url: "http://localhost:8000/getResults",
        //   params: {ModelName: this.modelNameSelected},
        //   method: "GET",
        //   responseType: 'blob',
        //   headers: headersList,
        //   }
          
        axios.request(reqOptions).then((response) => {
            var fileURL = window.URL.createObjectURL(new Blob([response.data]));
            var fileLink = document.createElement('a');
            fileLink.href = fileURL;
            fileLink.setAttribute('download', this.modelNameSelected + '.zip');
            document.body.appendChild(fileLink);
            fileLink.click();

        });

        this.resultsLoading = false;
      },
      async getPlot() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/getPlot",
          params: {ModelName: this.modelNameSelected},
          method: "GET",
          headers: headersList,
          }

        this.loading = true
        await axios.request(reqOptions).then(response => (
        this.message = response.data[1].split(','),
          this.plot[0].x = response.data[0].split(','),
          this.plot[0].y = response.data[1].split(',')))
        this.snackbar = true
        this.viewId = 2
        this.loading = false
      },
      showResults() {
        window.open("https://cara.dlr.de/enginframe/vdi/vdi.xml", "_blank");
      },
      async getLogFile() {
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/getLogFile",
          params: {ModelName: this.modelNameSelected,
                  Cluster: this.job.cluster},
          method: "GET",
          headers: headersList,
          }

        this.loading = true
        await axios.request(reqOptions).then(response => (
          this.yamlOutput = response.data))
        this.loading = false
      },
      writeInputFile() {
        let reqOptions = {
          url: "http://localhost:8000/writeInputFile",
          params: {ModelName: this.modelNameSelected,
                  InputString: this.yamlOutput,
                  FileType: this.solver.filetype},
          method: "POST",
          }

        axios.request(reqOptions).then(response => (this.message = response.data))
      },
      deleteModel() {
        this.dialogDeleteModel = false;
        
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/deleteModel",
          params: {ModelName: this.modelNameSelected},
          method: "POST",
          headers: headersList,
          }
          
        axios.request(reqOptions).then(response => (this.message = response.data))

        reqOptions = {
          url: "http://localhost:8000/deleteModelFromCluster",
          params: {ModelName: this.modelNameSelected,
                  Cluster: this.job.cluster},
          method: "POST",
          headers: headersList,
          }
          
        axios.request(reqOptions).then(response => (this.message = response.data))
        this.snackbar=true
      },
      deleteUserData() {
        this.dialogDeleteUserData = false;
        
        let headersList = {
        'Cache-Control': 'no-cache'
        }

        let reqOptions = {
          url: "http://localhost:8000/deleteUserData",
          // params: {},
          method: "POST",
          headers: headersList,
          }
          
        axios.request(reqOptions).then(response => (this.message = response.data))
        reqOptions = {
          url: "http://localhost:8000/deleteUserDataFromCluster",
          params: {Cluster: this.job.cluster},
          method: "POST",
          headers: headersList,
          }
          
        axios.request(reqOptions).then(response => (this.message = response.data))
        this.snackbar=true
      },
      addMaterial() {
        this.materials.push({
          id: this.nextMaterialId++,
          Name: "Material"+(this.nextMaterialId-1),
          Parameter: {}
        })
      },
      removeMaterial(index) {
        this.materials.splice(index, 1)
      },
      addDamage() {
        this.damages.push({
          id: this.nextdamageId++,
          Name: "Damage"+(this.nextdamageId-1),
          Parameter: {}
        })
      },
      removeDamage(index) {
        this.damages.splice(index, 1)
      },
      addBlock() {
        this.blocks.push({
          id: this.nextBlockId++,
          Name: "block_"+(this.nextBlockId-1)
        })
      },
      removeBlock(index) {
        this.blocks.splice(index, 1)
      },
      addCondition() {
        this.boundaryConditions.push({
          id: this.nextBoundaryConditionId++,
          Name: "BC_"+(this.nextBoundaryConditionId-1)
        })
      },
      removeCondition(index) {
        this.boundaryConditions.splice(index, 1)
      },
      addCompute() {
        this.computes.push({
          id: this.nextComputeId++,
          Name: "Compute"+(this.nextComputeId-1)
        })
      },
      removeCompute(index) {
        this.computes.splice(index, 1)
      },
      addOutput() {
        this.outputs.push({
          id: this.nextOutputId++,
          Name: "Output"+(this.nextOutputId-1)
        })
      },
      removeOutput(index) {
        this.outputs.splice(index, 1)
      },
      showModelImg() {
        switch (this.modelNameSelected) {
        case 'GIICmodel':  
          this.modelImg = GIICmodelImage;
          break;
        case 'DCBmodel':  
          this.modelImg = DCBmodelImage;
          break;
        case 'Dogbone':  
          this.modelImg = DogboneImage;
          break;
        }
        this.viewId = 0
      },
      changeToXml() {
        if(this.job.cluster=='FA-Cluster'){
          this.solver.filetype = 'xml'
        }
        else{
          this.solver.filetype = 'yaml'
        }
      },
      checkInputs() {
        if (this.length && this.width) {
          return true;
        }

        this.errors = [];

        if (!this.length) {
          this.errors.push('Length required');
        }
        if (!this.width) {
          this.errors.push('Width required');
        }

        this.message=this.errors.join('\n')

        this.snackbar=true

        return false;
      },
    },
  }