<template>
  <div style="height:calc(100% - 60px);">
    <div class="row">
      <div style="width: 200px;">
          <q-btn v-if="!modelData.modelownModel" flat icon="fas fa-sync-alt" @click="viewPointData">
            <q-tooltip>
              Reload Model
            </q-tooltip>
          </q-btn>
          <q-btn v-if="!modelData.modelownModel" flat icon="fas fa-expand" @click="$refs.view.resetCamera()">
            <q-tooltip>
              Reset Camera
            </q-tooltip>
          </q-btn>
      </div>
      <q-space></q-space>
      <div style="min-width: 100px; margin-right:20px">
        <q-slider
          v-model="radius"
          :min="0.01"
          :max="2"
          :step="0.01"
          label
          :label-value="'Radius: ' + radius"
          @change="updatePoints"
          color="gray"
        ></q-slider>
      </div>
      <!-- <div class="col" style="width: 100px;">
      </div> -->
      <div style="min-width: 100px;">
        <q-slider
          v-model="resolution"
          :min="3"
          :max="20"
          :step="1"
          label
          :label-value="'Resolution: ' + resolution"
          color="gray"
        ></q-slider>
      </div>
    </div>
    <vtk-view
      ref="view"
      :background="[45/255, 45/255, 45/255]"
    >
      <div v-if="viewStore.bondFilterPoints[0].bondFilterPointString.length!=0">
        <q-list
          
          v-for="bondFilterPoint in viewStore.bondFilterPoints"
          :key="bondFilterPoint.id"
        >
          <vtk-geometry-representation>
            <vtk-polydata
              :points="bondFilterPoint.bondFilterPointString"
              :polys="[4,0,1,2,3]"
            >
              <vtk-point-data>
                <vtk-data-array
                  registration="setScalars"
                  name="temperature"
                  :values="[.8,.8,.8,.8]"
                />
              </vtk-point-data>
            </vtk-polydata>
          </vtk-geometry-representation>
        </q-list>
      </div>
      <vtk-glyph-representation>
        <vtk-polydata :points="viewStore.filteredPointString">
          <vtk-cell-data>
            <vtk-data-array
              registration="setScalars"
              name="scalars"
              :values="viewStore.filteredBlockIdString"
              :state="{ rangeMax: 12}"
            />
          </vtk-cell-data>
        </vtk-polydata>
        <vtk-algorithm
          vtkClass="vtkSphereSource"
          :state="{ phiResolution: resolution, thetaResolution: resolution, radius: radius}"
          :port="1"
        />
      </vtk-glyph-representation>
    </vtk-view>
    </div>
</template>

<script>
    import { inject, computed, defineComponent } from 'vue'
    import { useViewStore } from 'stores/view-store';
    import { useModelStore } from 'stores/model-store';
    
    export default defineComponent({
        name: 'ModelView',
        components:{
        },
        setup() {
            const viewStore = useViewStore();
            const modelStore = useModelStore();
            const modelData = computed(() => modelStore.modelData)
            const bus = inject('bus')
            return {
                viewStore,
                modelData,
                bus,
            }
        },
        created() {
            this.bus.on('viewPointData', () => {
                console.log("viewPointData")
                this.viewPointData()
            })
            this.bus.on('filterPointData', () => {
                this.filterPointData()
            })
        },
        data() {
            return {
              resolution: 6,
              radius: 0.2,
              multiplier: 1,
              pointString: [1, 0, 0],
              blockIdString: [1],
            };
        }, 
        mounted(){
            this.viewPointData()
        },
        methods: {
          async viewPointData() {
            console.log("viewPointData")
            this.viewStore.modelLoading = true;

            await this.getPointDataAndUpdateDx();
            console.log(this.viewStore.dx_value)
            this.radius = this.viewStore.dx_value.toFixed(3);
            await this.updatePoints();

            this.viewStore.modelLoading = false;
            // console.log(this.$refs)
            this.$refs.view.resetCamera();
          },
          filterPointData() {
            var idx = 0;
            this.viewStore.filteredBlockIdString = [];
            this.viewStore.filteredPointString = [];
            for (var i = 0; i < this.blockIdString.length; i++) {
              if (
                this.modelData.blocks[parseInt(this.blockIdString[i] * this.modelData.blocks.length - 1)]
                  .show
              ) {
                this.viewStore.filteredBlockIdString[idx] = this.blockIdString[i];
                for (var j = 0; j < 3; j++) {
                  this.viewStore.filteredPointString[idx * 3 + j] =
                    this.pointString[i * 3 + j] * this.multiplier;
                }
                idx += 1;
              }
            }
          },
          async updatePoints() {
            this.viewStore.modelLoading = true;
            console.log(this.radius)
            if (this.radius < 0.01) {
              this.multiplier = (1 - this.radius / 0.5) * 30;
              this.radius=0.01
              this.filterPointData();
            } else if (this.radius <= 0.2) {
              this.multiplier = (1 - this.radius / 0.5) * 30;
              this.filterPointData();
            } else {
              this.multiplier = 1;
              this.filterPointData();
            }
            console.log(this.radius)
            this.viewStore.modelLoading = false;
          },
          async getPointDataAndUpdateDx() {

            let params = {
                model_name: this.modelData.model.modelNameSelected,
                own_model: this.modelData.model.ownModel,
                own_mesh: this.modelData.model.ownMesh,
                mesh_file: this.modelData.model.meshFile
            }
              this.$api.get('/getPointData', {params})
              .then((response) => {
                  this.pointString = response.data.data[0].split(",")
                  this.blockIdString = response.data.data[1].split(",")
                  this.$q.notify({
                      message: response.data.message,
                  })
              })
              .catch(() => {
                  this.$q.notify({
                      type: 'negative',
                      message: 'Loading failed',
                  })
              })

            if (!this.modelData.model.ownModel) {
              console.log(this.modelData.model.height)
              console.log(this.modelData.model.discretization)
              this.viewStore.dx_value =
                this.modelData.model.height / (2 * parseInt(this.modelData.model.discretization / 2) + 1);
              console.log(this.viewStore.dx_value)
            } else if (this.modelData.model.modelNameSelected == "Smetana") {
              let numOfPlys = 8;
              this.viewStore.dx_value =
                (this.modelData.model.height * numOfPlys) /
                (2 * parseInt(this.modelData.model.discretization / 2) + 1);
            } else {
              this.viewStore.dx_value = Math.hypot(
                parseFloat(this.pointString[3]) - parseFloat(this.pointString[0]),
                parseFloat(this.pointString[4]) - parseFloat(this.pointString[1]),
                parseFloat(this.pointString[5]) - parseFloat(this.pointString[2])
              );
            }

            // if (this.modelData.model.modelNameSelected == "Smetana") {
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
        },
    })
</script>

<style>
.viewport {
  height: 100%;
  width: 100%;
}
</style>
