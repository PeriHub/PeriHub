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
            const INIT = () => viewStore.INIT();
            const ANIMATE = () => viewStore.ANIMATE();
            const RESIZE = () => viewStore.RESIZE();
            const modelStore = useModelStore();
            const modelData = computed(() => modelStore.modelData)
            const bus = inject('bus')
            return {
                viewStore,
                INIT,
                ANIMATE,
                RESIZE,
                modelData,
                bus,
            }
        },
        created() {
            this.bus.on('viewPointData', () => {
                this.viewPointData()
            })
        },
        data() {
            return {
                resolution: 6,
                radius: 0.2,
            };
        }, 
        mounted() {
            console.log(this.$refs.viewport.offsetHeight)
            console.log(this.$el)
            let el =this.$refs.viewport
            this.INIT({
              width: this.$refs.viewport.offsetWidth,
              height: this.$refs.viewport.offsetHeight,
              el: this.$refs.viewport
            }).then(() => {
              this.ANIMATE();
              window.addEventListener(
                  "resize",
                  () => {
                  this.RESIZE({
                      width: this.$refs.viewport.offsetWidth,
                      height: this.$refs.viewport.offsetHeight
                  });
                  },
                  true
              );
            });
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
