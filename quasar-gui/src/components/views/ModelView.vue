<template>
    <div class="viewport" ref="viewport"></div>
    <!-- <vtk-view
      ref="view"
      :background="[45/255, 45/255, 45/255]"
    >
      <v-list
        v-for="bondFilterPoint in bondFilterPoints"
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
      </v-list>
      <vtk-glyph-representation>
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
          :port="1"
        />
      </vtk-glyph-representation>
    </vtk-view> -->
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
            };
        }, 
        mounted() {
        },
        methods: {
            async viewPointData() {
        this.viewStore.modelLoading = true;
        this.viewStore.viewId = 1;

        await this.getPointDataAndUpdateDx();

        this.radius = this.dx_value.toFixed(2);
        this.updatePoints();

        this.viewStore.modelLoading = false;
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
    updatePoints() {
      this.viewStore.modelLoading = true;
      if (this.radius <= 0.2) {
        this.multiplier = (1 - this.radius / 0.5) * 30;
        this.filterPointData();
      } else {
        this.multiplier = 1;
        this.filterPointData();
      }
      this.viewStore.modelLoading = false;
    },
    async getPointDataAndUpdateDx() {

        api.get('/getPointData',  
        { model_name: this.modelData.model.modelNameSelected,
          own_model: this.modelData.model.ownModel,
          own_mesh: this.modelData.model.ownMesh,
          mesh_file: this.modelData.model.meshFile})
        .then((response) => {
            this.pointString = response.data[0].split(",")
            this.blockIdString = response.data[1].split(",")
            this.$q.notify({
                color: 'positive',
                position: 'top',
                message: response.data,
                icon: 'report_problem'
            })
        })
        .catch(() => {
            this.$q.notify({
                color: 'negative',
                position: 'top',
                message: 'Loading failed',
                icon: 'report_problem'
            })
        })

      if (!this.modelData.model.ownModel) {
        this.dx_value =
          this.modelData.model.height / (2 * parseInt(this.modelData.model.discretization / 2) + 1);
      } else if (this.modelData.model.modelNameSelected == "Smetana") {
        let numOfPlys = 8;
        this.dx_value =
          (this.modelData.model.height * numOfPlys) /
          (2 * parseInt(this.modelData.model.discretization / 2) + 1);
      } else {
        this.dx_value = Math.hypot(
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
