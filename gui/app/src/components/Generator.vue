<template>

<v-container fluid style="height: 94vh;">
<splitpanes>
  <pane min-size="15" style="height: 94vh">
    <v-subheader>
      
          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="saveData">
                <i class="fas fa-save"></i>
            </v-btn>
          </template>
            <span>Save as JSON</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="readData">
                <i class="fas fa-upload"></i>
            </v-btn>
          </template>
            <span>Load JSON</span>
          </v-tooltip>
          <input
            type="file"
            style="display: none"
            ref="fileInput"
            accept="application/json"
            @change="onFilePicked"/>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="resetData">
                <i class="fas fa-undo"></i>
            </v-btn>
          </template>
            <span>Reset Data</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="generateModel">
                <i class="fas fa-cogs"></i>
            </v-btn>
          </template>
            <span>Generate Model</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="saveModel">
                <i class="fas fa-download"></i>
            </v-btn>
          </template>
            <span>Download Modelfiles</span>
          </v-tooltip>
    </v-subheader>
      <!-- <v-virtual-scroll
            :items="Array.from({length: 9}).map((_, index) => index)"
            :item-height="50"
            height=100vh
          > -->
    <!-- <v-container> -->
      <v-list style="height: 90vh; overflow-y: scroll">
  <!-- <v-list-item-group> -->
    <!-- <v-list-item> -->
    <v-card>
          <v-expansion-panels height=45vh>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Model</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
              <v-select 
                class="textfield-col"
                :items="modelName"
                v-model="modelNameSelected"
                @change="showModelImg"
                label="ModelName"
                outlined></v-select>
              <v-text-field 
                class="textfield-col"
                value=50
                v-model="length"
                :rules="[rules.required, rules.number]"
                label="Length"
                outlined></v-text-field>
              <v-text-field 
                class="textfield-col"
                value=10
                v-model="width"
                label="Width"
                outlined></v-text-field>
              <v-text-field 
                class="textfield-col"
                value=4.95
                v-model="height"
                label="Height"
                outlined></v-text-field>
              <v-text-field 
                class="textfield-col"
                value=11
                v-model="discretization"
                label="Discretization"
                outlined></v-text-field>
                <v-switch
                  class="checkbox-col"
                  v-model="twoDimensional"
                  label="Two Dimensional"
                ></v-switch>
                <v-switch
                  v-model="rotatedAngles"
                  label="Rotated Angles"
                ></v-switch>
                <v-row v-show="rotatedAngles">
                  <v-col class="textfield-col">
                    <v-text-field 
                      v-model=angles[0]
                      label="Angle 0"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col">
                    <v-text-field 
                      v-model=angles[1]
                      label="Angle 1"
                      outlined></v-text-field>
                  </v-col>
                </v-row>
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Material</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list v-for="material, index in materials" :key="material.id"
                style="padding: 0px">
                  <v-container v-bind:style="(material.id % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                    <h4>Material {{material.id}}</h4>
                    <v-row>
                      <v-col class="textfieldlist-col">
                        <v-text-field
                          v-model=material.Name
                          :rules="[rules.required, rules.name]"
                          label="Material Name"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfieldlist-col">
                        <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                          <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeMaterial(index)">
                              <i class="fas fa-trash-alt"></i>
                          </v-btn>
                          </template>
                            <span>Remove Material</span>
                        </v-tooltip>
                      </v-col>
                    </v-row>
                    <v-select class="textfield-col"
                      :items="materialModelName"
                      v-model=material.MatType
                      label="Material Model Name"
                      outlined></v-select>
                    <v-row>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=material.bulkModulus
                          label="Bulk Modulus"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=material.youngsModulus
                          label="Young's Modulus"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=material.poissonsRatio
                          label="Poisson's Ratio"
                          outlined></v-text-field>
                      </v-col>
                    </v-row>
                    <v-switch
                      v-model=material.tensionSeparation
                      :label="`Tension Separation`"
                    ></v-switch>
                    <v-select
                      :items="materialSymmetry"
                      v-model=material.materialSymmetry
                      v-show="material.MatType=='Linear Elastic Correspondence'"
                      label="Material Model Name"
                      outlined></v-select>
                      <v-container>
                        <v-row>
                          <li v-for="(params, name) in material.Parameter" :key="params.index">
                            <v-text-field  class="textfield-col"
                              style="padding-right: 10px"
                              v-model="params.value"
                              :label="name"
                              :rules="[rules.required, rules.number]"
                              outlined></v-text-field>
                          </li>
                        </v-row>
                      </v-container>
                    <v-select class="textfield-col"
                      :items="stabilizatonType"
                      v-model=material.stabilizatonType
                      label="Stabilizaton Type"
                      outlined></v-select>
                    <v-text-field class="textfield-col"
                      v-model=material.thickness
                      label="Thickness"
                      outlined></v-text-field>
                    <v-text-field class="textfield-col"
                      v-model=material.hourglassCoefficient
                      label="Hourglass Coefficient"
                      outlined></v-text-field>
                    <v-text-field class="textfield-col"
                      v-show="material.MatType=='Elastic Plastic Hypoelastic Correspondence'"
                      v-model=material.actualHorizon
                      label="Actual Horizon"
                      outlined></v-text-field>
                    <v-text-field class="textfield-col"
                      v-show="material.MatType=='Elastic Plastic Hypoelastic Correspondence'"
                      v-model=material.yieldStress
                      label="Yield Stress"
                      outlined></v-text-field>
                  </v-container>
                  <v-divider></v-divider>
                </v-list>
                <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                    <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addMaterial">
                        <i class="fas fa-plus"></i>
                    </v-btn>
                  </template>
                    <span>Add Material</span>
                </v-tooltip>
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Damage Models</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list v-for="damage, index in damages" :key="damage.id"
                style="padding: 0px">
                  <v-container v-bind:style="(damage.id % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                    <v-row>
                      <h4>Damage Model{{damage.id}}</h4>
                    </v-row>
                    <v-row>
                      <v-col class="textfieldlist-col">
                        <v-text-field
                          v-model=damage.Name
                          label="Damage Name"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfieldlist-col">
                        <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                          <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeDamage(index)">
                              <i class="fas fa-trash-alt"></i>
                          </v-btn>
                          </template>
                            <span>Remove Damage Model</span>
                        </v-tooltip>
                      </v-col>
                    </v-row>
                    <v-select class="textfield-col"
                      :items="damageModelName"
                      v-model=damage.damageModel
                      label="Damage Model Name"
                      outlined></v-select>
                    <v-row>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=damage.criticalStretch
                          label="Critical Stretch"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=damage.criticalEnergy
                          label="Critical Energy"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfield-col">
                        <v-text-field 
                          v-model=damage.interblockdamageEnergy
                          label="Interblock Damage Energy"
                          outlined></v-text-field>
                      </v-col>
                    </v-row>
                    <v-switch
                      v-model=damage.onlyTension
                      label="Only Tension"
                    ></v-switch>
                    <v-select class="textfield-col"
                      :items="stabilizatonType"
                      v-model=damage.stabilizatonType
                      label="Stabilizaton Type"
                      outlined></v-select>
                    <v-switch
                      v-model=damage.detachedNodesCheck
                      label="Detached Nodes Check"
                    ></v-switch>
                    <v-text-field class="textfield-col"
                      v-model=damage.thickness
                      label="Thickness"
                      outlined></v-text-field>
                    <v-text-field class="textfield-col"
                      v-model=damage.hourglassCoefficient
                      label="Hourglass Coefficient"
                      outlined></v-text-field>
                  </v-container>
                  <v-divider></v-divider>
                </v-list>
                <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                    <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addDamage">
                        <i class="fas fa-plus"></i>
                    </v-btn>
                  </template>
                    <span>Add Damage Model</span>
                </v-tooltip>
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Blocks</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list v-for="block in blocks" :key="block.id">
                  <!-- <h4>block_{{block.id}}</h4> -->
                  <v-row >
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-text-field
                        v-model=block.Name
                        label="Block Name"
                        outlined></v-text-field>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-select
                        :items= materials
                        item-text="Name"
                        v-model=block.material
                        label="Material"
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="3">
                      <v-select
                        :items=damages
                        item-text="Name"
                        v-model=block.damageModel
                        label="Damage Model"
                        clearable
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-select
                        :items=blocks
                        item-text="id"
                        v-model=block.interface
                        label="Interface"
                        clearable
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-checkbox
                        v-model=block.show
                        label="Show"
                        @change="filterPointData"
                        outlined></v-checkbox>
                    </v-col>
                    <!-- <v-col class="textfieldlist-col"
                      cols="12"
                      sm="1">
                      <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                        <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeBlock(index)">
                            <i class="fas fa-trash-alt"></i>
                        </v-btn>
                        </template>
                          <span>Remove Block</span>
                      </v-tooltip>
                    </v-col> -->
                  </v-row>
                  <v-divider></v-divider>
                </v-list>
                <!-- <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                    <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addBlock">
                        <i class="fas fa-plus"></i>
                    </v-btn>
                  </template>
                    <span>Add Block</span>
                </v-tooltip> -->
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Boundary Conditions</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-list v-for="boundaryCondition, index in boundaryConditions" :key="boundaryCondition.id">
                  <!-- <h4>block_{{block.id}}</h4> -->
                  <v-row>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-text-field
                        v-model=boundaryCondition.Name
                        label="Name"
                        outlined></v-text-field>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="3">
                      <v-select
                        :items= boundarytype
                        item-text="Name"
                        v-model=boundaryCondition.boundarytype
                        label="Type"
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-select
                        :items=blocks
                        item-text="id"
                        v-model=boundaryCondition.blockId
                        label="Block Id"
                        clearable
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-select
                        :items=coordinate
                        v-model=boundaryCondition.coordinate
                        label="Coordinate"
                        clearable
                        outlined></v-select>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="2">
                      <v-text-field
                        v-model=boundaryCondition.value
                        label="Value"
                        outlined></v-text-field>
                    </v-col>
                    <v-col class="textfieldlist-col"
                      cols="12"
                      sm="1">
                      <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                        <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeCondition(index)">
                            <i class="fas fa-trash-alt"></i>
                        </v-btn>
                        </template>
                          <span>Remove Condition</span>
                      </v-tooltip>
                    </v-col>
                  </v-row>
                  <v-divider></v-divider>
                </v-list>
                <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                    <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addCondition">
                        <i class="fas fa-plus"></i>
                    </v-btn>
                  </template>
                    <span>Add Condition</span>
                </v-tooltip>
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Output</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-row>
                  <h4>Compute Parameters</h4>
                </v-row>
                <v-container>
                  <v-list v-for="compute, index in computes" :key="compute.id">
                    <v-row>
                      <v-col class="textfieldlist-col"
                        cols="12"
                        sm="3">
                        <v-text-field
                          v-model=compute.Name
                          label="Name"
                          outlined></v-text-field>
                      </v-col>
                      <v-col class="textfieldlist-col"
                        cols="12"
                        sm="2">
                        <v-select
                          :items=variables
                          v-model=compute.variable
                          label="Variable"
                          outlined></v-select>
                      </v-col>
                      <v-col class="textfieldlist-col"
                        cols="12"
                        sm="2">
                        <v-select
                          :items=calculationType
                          v-model=compute.calculationType
                          label="Calculation Type"
                          outlined></v-select>
                      </v-col>
                      <v-col class="textfieldlist-col"
                        cols="12"
                        sm="2">
                        <v-select
                          :items=blocks
                          item-text="Name"
                          v-model=compute.blockName
                          label="Block Id"
                          clearable
                          outlined></v-select>
                      </v-col>
                      <v-col class="textfieldlist-col"
                        cols="12"
                        sm="1">
                        <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                          <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeCompute(index)">
                              <i class="fas fa-trash-alt"></i>
                          </v-btn>
                          </template>
                            <span>Remove Compute</span>
                        </v-tooltip>
                      </v-col>
                    </v-row>
                    <v-divider></v-divider>
                  </v-list>
                </v-container>
                <v-row>
                  <v-col
                  class="textfield-col">
                    <v-tooltip bottom  class="textfield-col"><template v-slot:activator="{ on, attrs }">
                        <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addCompute">
                            <i class="fas fa-plus"></i>
                        </v-btn>
                      </template>
                        <span>Add Compute</span>
                    </v-tooltip>
                  </v-col>
                </v-row>                <v-divider></v-divider>
                <v-list v-for="output, index in outputs" :key="output.id"
                style="padding: 0px">
                  <v-container v-bind:style="(output.id % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                  <v-row>
                    <h4>Output {{output.id}}</h4>
                  </v-row>
                  <v-row>
                    <v-col
                    class="textfield-col">
                      <v-text-field
                        v-model=output.Name
                        label="Name"
                        outlined></v-text-field>
                    </v-col>
                    <v-col class="textfield-col">
                      <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                        <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="removeOutput(index)">
                            <i class="fas fa-trash-alt"></i>
                        </v-btn>
                        </template>
                          <span>Remove Output</span>
                      </v-tooltip>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.Displacement
                        label="Displacement"></v-checkbox>
                    </v-col>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.Force
                        label="Force"></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.Damage
                        label="Damage"></v-checkbox>
                    </v-col>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.Partial_Stress
                        label="Partial_Stress"></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.External_Force
                        label="External_Force"></v-checkbox>
                    </v-col>
                    <v-col
                    class="checkbox-col"
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.External_Displacement
                        label="External_Displacement"></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.Number_Of_Neighbors
                        label="Number_Of_Neighbors"></v-checkbox>
                    </v-col>
                    <!-- <v-col
                    cols="15"
                    sm="5"
                    md="5">
                      <v-checkbox class="shrink mr-0 mt-0"
                        v-model=output.External_Displacement
                        label="External_Displacement"></v-checkbox>
                    </v-col> -->
                  </v-row>
                  <v-text-field class="textfield-col"
                  v-model=output.Frequency
                  label="Output Frequency"
                  outlined></v-text-field>
                  <v-text-field class="textfield-col"
                  v-model=output.InitStep
                  label="Initial Output Step"
                  outlined></v-text-field>
                  </v-container>
                  <v-divider></v-divider>
                </v-list>
                <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
                    <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="addOutput">
                        <i class="fas fa-plus"></i>
                    </v-btn>
                  </template>
                    <span>Add Output</span>
                </v-tooltip>
              </v-expansion-panel-content>
            </v-expansion-panel>
          <v-divider></v-divider>
          <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Solver</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-row>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.initialTime"
                      label="Initial Time"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.finalTime"
                      label="Final Time"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-checkbox
                      v-model="solver.verbose"
                      label="Verbose"
                      outlined></v-checkbox>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="solvertype"
                      v-model="solver.solvertype"
                      label="Solvertype"
                      outlined></v-select>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.safetyFactor"
                      label="Safety Factor"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.numericalDamping"
                      label="Numerical Damping"
                      outlined></v-text-field>
                  </v-col>
                </v-row>
                <v-row v-show="solver.solvertype=='NOXQuasiStatic'">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="peridgimPreconditioner"
                      v-model="solver.peridgimPreconditioner"
                      label="Peridgim Preconditioner"
                      outlined></v-select>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="nonlinearSolver"
                      v-model="solver.nonlinearSolver"
                      label="Nonlinear Solver"
                      outlined></v-select>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.numberofLoadSteps"
                      label="Number of Load Steps"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.maxSolverIterations"
                      label="Max Solver Iterations"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.relativeTolerance"
                      label="Relative Tolerance"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.maxAgeOfPrec"
                      label="Max Age Of Prec"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="directionMethod"
                      v-model="solver.directionMethod"
                      label="Direction Method"
                      outlined></v-select>
                  </v-col>
                </v-row>
                <v-row v-show="solver.solvertype=='NOXQuasiStatic'">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="jacobianOperator"
                      v-model="solver.newton.jacobianOperator"
                      label="Jacobian Operator"
                      outlined></v-select>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="preconditioner"
                      v-model="solver.newton.preconditioner"
                      label="Preconditioner"
                      outlined></v-select>
                  </v-col>
                </v-row>
                <v-row v-show="solver.solvertype=='NOXQuasiStatic'">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-select
                      :items="lineSearchMethod"
                      v-model="solver.lineSearchMethod"
                      label="Line Search Method"
                      outlined></v-select>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-checkbox
                      v-model="solver.verletSwitch"
                      label="Switch to Verlet"
                      outlined></v-checkbox>
                  </v-col>
                </v-row>
                <v-row v-show="solver.verletSwitch & solver.solvertype=='NOXQuasiStatic'">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.verlet.safetyFactor"
                      label="Safety Factor"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.verlet.numericalDamping"
                      label="Numerical Damping"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.verlet.outputFrequency"
                      label="Output Frequency"
                      outlined></v-text-field>
                  </v-col>
                </v-row>
                <v-row v-show="solver.solvertype=='Verlet'">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-checkbox
                      v-model="solver.adaptivetimeStepping"
                      label="Adaptive Time Stepping"
                      outlined></v-checkbox>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-checkbox
                      v-model="solver.stopAfterDamageInitation"
                      label="Stop after damage initiation"
                      outlined></v-checkbox>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-checkbox
                      v-model="solver.stopBeforeDamageInitation"
                      label="Stop before damage initiation"
                      outlined></v-checkbox>
                  </v-col>
                </v-row>
                <v-row v-show="solver.solvertype=='Verlet' & solver.adaptivetimeStepping">
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.adapt.stableStepDifference"
                      label="Stable Step Difference"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.adapt.maximumBondDifference"
                      label="Maximum Bond Difference"
                      outlined></v-text-field>
                  </v-col>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="3">
                    <v-text-field 
                      v-model="solver.adapt.stableBondDifference"
                      label="Stable Bond Difference"
                      outlined></v-text-field>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col class="textfield-col"
                    cols="12"
                    sm="12">
                  <v-select
                    :items="filetype"
                    v-model="solver.filetype"
                    v-show="job.cluster=='Cara'"
                    label="Filetype"
                    outlined></v-select>
                  </v-col>
                </v-row>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel>
              <v-expansion-panel-header>
                <h2>Job</h2>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-select class="textfield-col"
                  :items="cluster"
                  v-model="job.cluster"
                  @change="changeToXml"
                  label="Cluster"
                  outlined></v-select>
                <v-text-field class="textfield-col"
                  v-model="job.tasks"
                  label="Tasks"
                  outlined></v-text-field>
                <v-text-field class="textfield-col"
                  v-model="job.time"
                  label="Time"
                  outlined></v-text-field>
                <v-text-field class="textfield-col"
                  v-model="job.user"
                  label="User"
                  outlined></v-text-field>
                <v-text-field class="textfield-col"
                  v-model="job.account"
                  label="Account"
                  outlined></v-text-field>
                <v-text-field class="textfield-col"
                  v-model="job.mail"
                  label="Mail"
                  outlined></v-text-field>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
    </v-card>
          <!-- </v-list-item> -->
  <!-- </v-list-item-group> -->
</v-list>
    <!-- </v-container> -->
  </pane>
  <pane min-size="40">
    <splitpanes horizontal style="height: 94vh">
      <pane size="55">
         <!-- <v-container> -->
        
        <v-subheader>
          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="copyModelToCluster">
                <i class="fas fa-share"></i>
            </v-btn>
          </template>
            <span>Copy Model to Cluster</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="runModel">
                <i class="fas fa-play"></i>
            </v-btn>
          </template>
            <span>Submit Model</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="cancelJob">
                <i class="fas fa-times"></i>
            </v-btn>
          </template>
            <span>Cancel Job</span>
          </v-tooltip>

            <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
              <v-btn class="my-btn" v-bind="attrs" v-on="on" 
                      @click="dialog = true"
                      :loading="resultsLoading"
                      :disabled="resultsLoading">
                  <i class="fas fa-download"></i>
              </v-btn>
              </template>
              <span>Download Results</span>
            </v-tooltip>

          <v-dialog
            v-model="dialog"
            persistent
            max-width="400"
          >
              <v-card>
                <v-card-title class="text-h5">
                  Download Results
                </v-card-title>
                <v-card-text>Do you want to retrieve all modelfiles, including the inputfiles and logdata or only the exodus results?</v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="green darken-1"
                    text
                    @click="saveResults(true)"
                  >
                    All data
                  </v-btn>
                  <v-btn
                    color="green darken-1"
                    text
                    @click="saveResults(false)"
                  >
                    Only the results
                  </v-btn>
                  <v-btn
                    color="red darken-1"
                    text
                    @click="dialog = false"
                  >
                    Cancel
                  </v-btn>
                </v-card-actions>
              </v-card>
          </v-dialog>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="showResults">
                <i class="fas fa-external-link-alt"></i>
            </v-btn>
          </template>
            <span>Show Results</span>
          </v-tooltip>

          <v-spacer/>
        </v-subheader>
        <v-card class="my-card"
        title='ModelView'
        elevation="0"
        height=88%
        width=100%
        margin=10px
        :loading="loading"
        color="#808080"
        >
        
        <v-card-title class="my-title" style="padding-top: 0px">
           

          <v-tooltip bottom class="my-btn"><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="viewPointData">
                <i class="fas fa-sync-alt"></i>
            </v-btn>
          </template>
            <span>Reload Model</span>
          </v-tooltip>

          <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
            <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="$refs.view.resetCamera()">
                <i class="fas fa-expand"></i>
            </v-btn>
          </template>
            <span>Reset Camera</span>
          </v-tooltip>

          <v-slider
            v-model="radius"
            label="Radius:"
            max="0.5"
            min="0.01"
            step="0.01"
            style="max-width: 200px"
            @change="updatePoints"
          ></v-slider>

          <v-slider
            v-model="resolution"
            label="Resolution:"
            max="20"
            min="3"
            step="1"
            style="max-width: 200px"
          ></v-slider>
        </v-card-title>
          <template slot="progress">
            <v-progress-linear
              color="deep-purple"
              height="10"
              indeterminate
            ></v-progress-linear>
          </template>
          <!-- <v-toolbar> -->
          <!-- </v-toolbar>
          <v-divider class="mx-4"></v-divider> -->
          
          <vtk-view
            v-if="showVtk"
            ref="view"
            :background="[0.5, 0.5, 0.5]">
            <vtk-glyph-representation >
              <vtk-polydata :points="filteredPointString">
                <vtk-cell-data>
                  <vtk-data-array
                    registration="setScalars"
                    name="scalars"
                    :values="filteredBlockIdString"
                    :state="{ rangeMax: 12}" 
                  />
                </vtk-cell-data>
              </vtk-polydata>
              <vtk-algorithm 
                vtkClass="vtkSphereSource" 
                :state="{ phiResolution: resolution, thetaResolution: resolution, radius: radius}" 
                port=1
              />
            </vtk-glyph-representation>
          </vtk-view>
          <v-img
            v-if="!showVtk"
            alt="DLR Logo"
            class="shrink mr-2"
            contain
            :src="modelImg"
            transition="scale-transition"
            width="100%"
          />
          <!-- <pdf v-if="!showVtk" :src="pdfPath" :background="[0.5, 0.5, 0.5]"
           style="display: inline-block; width: 100%; height=10%;"></pdf> -->
          <!-- <remote-component
            url="https://unpkg.com/vue-plotly@^1/dist/vue-plotly.umd.min.js"
            :data="[{ x: [0, 1, 2, 3], y: [1, 3, 3, 7], type: 'scatter' }]"
            :extract="library => library.Plotly" /> -->
          <!-- <remote-component url="http://localhost:8081/"
            :extract="extract" /> -->

        </v-card>

        <!-- </v-container> -->
      </pane>
      <pane size="45">
        <!-- <v-container> -->
        <v-subheader>
            <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
              <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="viewInputFile">
                  <i class="fas fa-sync-alt"></i>
              </v-btn>
            </template>
              <span>Reload Inputfile</span>
            </v-tooltip>

            <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
              <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="getLogFile">
                  <i class="fas fa-file"></i>
              </v-btn>
            </template>
              <span>Show LogFile</span>
            </v-tooltip>

            <v-tooltip bottom><template v-slot:activator="{ on, attrs }">
              <v-btn class="my-btn" v-bind="attrs" v-on="on" @click="writeInputFile">
                  <i class="fas fa-save"></i>
              </v-btn>
            </template>
              <span>Save Inputfile</span>
            </v-tooltip>
        </v-subheader>
        <!-- class="overflow-y-auto" -->
        <v-card class="my-card"
        title='YamlOutput'
        elevation="0"
        height=85%
        width=100%
        :loading="loading"
        flex
        >
          <template slot="progress">
            <v-progress-linear
              color="deep-purple"
              height="10"
              indeterminate
            ></v-progress-linear>
          </template>
          <!-- <v-toolbar> -->
          <!-- </v-toolbar>
          <v-divider class="mx-4"></v-divider> -->
            <prism-editor
              class="my-editor"
              v-model="yamlOutput"
              :highlight="highlighter"
              line-numbers
            ></prism-editor>
          <!-- <v-textarea
            v-model="yamlOutput"
            auto-grow
          ></v-textarea> -->
        </v-card>
        <!-- </v-container> -->
      </pane>
    </splitpanes>
  </pane>
</splitpanes>
    <!-- <v-row>
      <v-col
        class="d-flex"
        cols="12"
        sm="4">
        
      </v-col>
      <v-col
        class="d-flex"
        cols="12"
        sm="8">
       
      </v-col>
    </v-row> -->
    <v-snackbar
        v-model="snackbar"
      >
        <!-- <pre>{{message}}</pre> -->
        {{message}}
  
        <template v-slot:action="{ attrs }">
          <v-btn
            color="pink"
            text
            v-bind="attrs"
            @click="snackbar = false"
          >
            Close
          </v-btn>
        </template>
      </v-snackbar>
  </v-container>
</template>

<script>
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

  export default {
    name: 'ModelGenerator',
    components: {
      PrismEditor,
      Splitpanes,
      Pane,
      // pdf
      // RemoteComponent
    },
    data () {
      return {
        // Model
        modelName: ['GIICmodel', 'DCBmodel'],
        modelNameSelected: 'GIICmodel',
        length: 50,
        width: 10,
        height: 4.95,
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
          user: 'hess_ja',
          account: '2263032',
          mail: 'jan-timo.hesse@dlr.de',
        },
        cluster: ['Cara', 'FA-Cluster'],


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
        showVtk: false,
        modelImg: GIICmodelImage,
        jsonFIle: GIICmodelFile,
        dialog: false,
        errors: [],
        rules: {
          required: value => !!value || 'Required.',
          name: value => {
            const pattern = /^[A-Za-z0-9_]{1,15}/
            return pattern.test(value) || 'Invalid name.'
          },
          number: value => {
            // const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            // const pattern = /^-?[\d.]+e(-|\+)\d{1,2}/
            const pattern = /^[0-9.e-]{1,15}/
            return pattern.test(value) || 'Invalid number.'
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
                      "\"Length\":" + this.length + ",\n" +
                      "\"width\":" + this.width + ",\n" +
                      "\"height\":" + this.height + ",\n" +
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
        this.showVtk = true
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
          
        await axios.request(reqOptions).then((response) => {
            var fileURL = window.URL.createObjectURL(new Blob([response.data]));
            var fileLink = document.createElement('a');
            fileLink.href = fileURL;
            fileLink.setAttribute('download', 'results.zip');
            document.body.appendChild(fileLink);
            fileLink.click();

        });
        this.resultsLoading = false;
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
        }
        this.showVtk = false
      },
      changeToXml() {
        this.solver.filetype = 'xml'
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
</script>

<style>
/* required class */
.my-editor {
  /* we dont use `language-` classes anymore so thats why we need to add background and text color manually */
  background: #2d2d2d;
  color: #ccc;

  /* you must provide font-family font-size line-height. Example: */
  font-family: Fira code, Fira Mono, Consolas, Menlo, Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 5px;
}

/* optional class for removing the outline */
.prism-editor__textarea:focus {
  outline: none;
}

.textfield-col {
  height: 80px;
}

.textfieldlist-col {
  height: 110px;
}

.checkbox-col {
  height: 30px;
}

#v-list {
  padding-top: 0px;
}

.my-title {
  height: 50px;
  justify-content: flex-end;
  margin: 0 30px;
}

.my-card {
  margin: 10px;
}
/* .splitpanes {background-color: #f8f8f8;} */

.splitpanes__splitter {background-color: #ccc;position: relative;}
.splitpanes__splitter:before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  transition: opacity 0.4s;
  background-color: rgba(158, 158, 158, 0.3);
  opacity: 0;
  z-index: 1;
}
.splitpanes__splitter:hover:before {opacity: 1;}
.splitpanes--vertical > .splitpanes__splitter:before {left: -10px;right: -10px;height: 100%;}
.splitpanes--horizontal > .splitpanes__splitter:before {top: -10px;bottom: -10px;width: 100%;}
</style>