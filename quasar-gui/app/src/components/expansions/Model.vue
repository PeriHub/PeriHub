<template>
        <div>
            <q-select 
                class="my-select"
                :options="modelName"
                v-model="model.modelNameSelected"
                v-show="!model.ownModel"
                label="Model Name"
                standout
                dense
            ></q-select>
            <q-input 
                class="my-input"
                v-model="model.modelSubName"
                v-show="!model.ownModel"
                label="Model Subname"
                standout
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="model.modelNameSelected"
                v-show="model.ownModel"
                :rules="[rules.required]"
                label="Model Name"
                standout
                dense
            ></q-input>
            <q-input 
                class="my-input"
                v-model="model.meshFile"
                v-show="model.ownModel"
                :rules="[rules.required]"
                label="Mesh File"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.length"
                v-show="!model.ownModel & model.modelNameSelected!='RVE'"
                :rules="[rules.required, rules.float]"
                label="Length"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.cracklength"
                v-show="['GICmodel','GIICmodel','CompactTension', 'KICmodel', 'KIICmodel', 'ENFmodel'].includes(model.modelNameSelected)"
                :rules="[rules.required, rules.float]"
                label="Cracklength"
                standout
                dense
            ></q-input>
            <q-toggle
                class="my-toggle"
                v-model="model.notchEnabled"
                v-show="['CompactTension'].includes(model.modelNameSelected)"
                label="Notch enabled"
                dense
            ></q-toggle>
            <q-input
                class="my-input"
                v-model="model.width"
                v-show="!model.ownModel & model.modelNameSelected!='RVE' & !model.twoDimensional"
                :rules="[rules.required, rules.float]"
                label="Width"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.height"
                v-show="!model.ownModel & !['RVE','CompactTension','Smetana'].includes(model.modelNameSelected)"
                :rules="[rules.required, rules.float]"
                label="Height"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.height"
                v-show="!model.ownModel & ['Smetana'].includes(model.modelNameSelected)"
                :rules="[rules.required, rules.float]"
                label="Ply height"
                standout
                dense
            ></q-input>
            <q-input
                v-show="model.modelNameSelected=='Dogbone' & !model.ownModel"
                class="my-input"
                v-model="model.height2"
                :rules="[rules.required, rules.float]"
                label="Inner Height"
                standout
                dense
            ></q-input>
            <q-input
                v-show="model.modelNameSelected=='PlateWithHole' & !model.ownModel"
                class="my-input"
                v-model="model.radius"
                :rules="[rules.required, rules.float]"
                label="Radius"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.discretization"
                v-show="!model.ownModel & model.modelNameSelected!='RVE'"
                :rules="[rules.required, rules.int]"
                label="Discretization"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.horizon"
                v-show="model.ownModel"
                :rules="[rules.required, rules.posFloat]"
                label="Horizon"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.amplitudeFactor"
                v-show="!model.ownModel & model.modelNameSelected=='Smetana'"
                :rules="[rules.required, rules.posFloat]"
                label="Amplitude Factor"
                standout
                dense
            ></q-input>
            <q-input
                class="my-input"
                v-model="model.wavelength"
                v-show="!model.ownModel & model.modelNameSelected=='Smetana'"
                :rules="[rules.required, rules.posFloat]"
                label="Wavelength"
                standout
                dense
            ></q-input>
            <q-toggle
                class="my-toggle"
                v-show="model.modelNameSelected=='Dogbone' & !model.ownModel"
                v-model="model.structured"
                label="Structured"
                dense
            ></q-toggle>
            <q-toggle
                class="my-toggle"
                v-show="!model.ownModel & model.modelNameSelected!='RVE'"
                v-model="model.twoDimensional"
                label="Two Dimensional"
                dense
            ></q-toggle>
            <q-toggle
                class="my-toggle"
                v-model="model.rotatedAngles"
                v-show="!model.ownModel & model.modelNameSelected!='RVE' & model.modelNameSelected!='Dogbone'"
                label="Rotated Angles"
                dense
            ></q-toggle>
            <div class="row"
            v-show="model.rotatedAngles & !model.ownModel & model.modelNameSelected!='RVE' & model.modelNameSelected!='Dogbone'"
            >
                <div 
                            class="my-input">
                    <q-input
                    v-model="model.angles[0]"
                    label="Angle 0"
                    standout
                    dense
                    ></q-input>
                </div>
                <div 
                            class="my-input">
                    <q-input
                    v-model="model.angles[1]"
                    label="Angle 1"
                    standout
                    dense
                    ></q-input>
                </div>
                <div 
                            class="my-input">
                    <q-input
                    v-model="model.angles[2]"
                    label="Angle 2"
                    standout
                    dense
                    ></q-input>
                </div>
                <div 
                            class="my-input">
                    <q-input
                    v-model="model.angles[3]"
                    label="Angle 3"
                    standout
                    dense
                    ></q-input>
                </div>
            </div>
            <!-- <div v-show="model.modelNameSelected=='RVE' & !model.ownModel">
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.RVE.rve_fvc"
                    :rules="[rules.required, rules.float]"
                    label="rve_fvc"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.RVE.rve_radius"
                    :rules="[rules.required, rules.float]"
                    label="rve_radius"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.RVE.rve_lgth"
                    :rules="[rules.required, rules.float]"
                    label="rve_lgth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.RVE.rve_dpth"
                    :rules="[rules.required, rules.float]"
                    label="rve_dpth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.Mesh.mesh_fib"
                    :rules="[rules.required, rules.float]"
                    label="mesh_fib"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.Mesh.mesh_lgth"
                    :rules="[rules.required, rules.float]"
                    label="mesh_lgth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.Mesh.mesh_dpth"
                    :rules="[rules.required, rules.float]"
                    label="mesh_dpth"
                    standout
                    dense
                ></v-text-field>
                <v-text-field
                    
                            class="my-input"
                    v-model="micofam.Mesh.mesh_aa"
                    :rules="[rules.required]"
                    label="mesh_aa"
                    standout
                    dense
                ></v-text-field>
            </div> -->
    </div>  
</template>
  
<script>
    import { computed, defineComponent, inject } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { parseFromJson } from '../../utils/functions.js'
    import rules from "assets/rules.js";

    import KICmodelFile from "assets/models/KICmodel/KICmodel.json";
    import KIICmodelFile from "assets/models/KIICmodel/KIICmodel.json";
    import ENFmodelFile from "assets/models/ENFmodel/ENFmodel.json";
    import GIICmodelFile from "assets/models/GIICmodel/GIICmodel.json";
    import GICmodelFile from "assets/models/GICmodel/GICmodel.json";
    import DCBmodelFile from "assets/models/DCBmodel/DCBmodel.json";
    import DogboneFile from "assets/models/Dogbone/Dogbone.json";
    import KalthoffWinklerFile from "assets/models/Kalthoff-Winkler/Kalthoff-Winkler.json";
    import PlateWithHoleFile from "assets/models/PlateWithHole/PlateWithHole.json";
    import CompactTensionFile from "assets/models/CompactTension/CompactTension.json";
    import SmetanaFile from "assets/models/Smetana/Smetana.json";
  
    export default defineComponent({
        name: 'ModelSettings',
        setup() {
            const store = useModelStore();
            const model = computed(() => store.modelData.model)
            const bus = inject('bus')
            return {
                store,
                model,
                rules,
                bus
            }
        },
        created() {
            this.bus.on('resetData', () => {
                this.resetData()
            })
        },
        data() {
            return {
                modelName: [
                    "Dogbone",
                    "Kalthoff-Winkler",
                    "PlateWithHole",
                    "GICmodel",
                    "GIICmodel",
                    "KICmodel",
                    "KIICmodel",
                    "ENFmodel",
                    "DCBmodel",
                    "CompactTension",
                    "Smetana",
                    // "OwnModel",
                ],
            };
        },
        methods: {
            async resetData() {
                const jsonFile = {};
                // console.log(this.model.modelNameSelected);
                switch (this.model.modelNameSelected) {
                    case "GICmodel":
                    Object.assign(jsonFile, GICmodelFile);
                    break;
                    case "GIICmodel":
                    Object.assign(jsonFile, GIICmodelFile);
                    break;
                    case "KICmodel":
                    Object.assign(jsonFile, KICmodelFile);
                    break;
                    case "KIICmodel":
                    Object.assign(jsonFile, KIICmodelFile);
                    break;
                    case "ENFmodel":
                    Object.assign(jsonFile, ENFmodelFile);
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
                parseFromJson(this.store.modelData,jsonFile)
            },
        },
        watch: {
            'store.modelData.model.modelNameSelected': {
                handler() {
                    console.log(this.store.modelData.model.modelNameSelected)
                    this.bus.emit("showModelImg", this.store.modelData.model.modelNameSelected)
                    this.bus.emit("getStatus")
                    this.resetData()
                },
            },
        }
    })
</script>
  