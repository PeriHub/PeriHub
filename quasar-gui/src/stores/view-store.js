import { defineStore } from "pinia";
import {
  Scene,
  TrackballControls,
  PerspectiveCamera,
  WebGLRenderer,
  Color,
  FogExp2,
  CylinderBufferGeometry,
  MeshPhongMaterial,
  Mesh,
  DirectionalLight,
  AmbientLight,
  LineBasicMaterial,
  Geometry,
  Vector3,
  Line,
} from "three-full";

export const useViewStore = defineStore("view", {
  state: () => ({
    viewId: 1,
    modelLoading: false,
    width: 0,
    height: 0,
    camera: null,
    controls: null,
    scene: null,
    renderer: null,
    axisLines: [],
    pyramids: [],
  }),
  actions: {
    SET_VIEWPORT_SIZE(width, height) {
      this.width = width;
      this.height = height;
    },
    INITIALIZE_RENDERER(el) {
      this.renderer = new WebGLRenderer({ antialias: true });
      this.renderer.setPixelRatio(window.devicePixelRatio);
      this.renderer.setSize(this.width, this.height);
      el.appendChild(this.renderer.domElement);
    },
    INITIALIZE_CAMERA() {
      this.camera = new PerspectiveCamera(
        // 1. Field of View (degrees)
        60,
        // 2. Aspect ratio
        this.width / this.height,
        // 3. Near clipping plane
        1,
        // 4. Far clipping plane
        1000
      );
      this.camera.position.z = 500;
    },
    INITIALIZE_CONTROLS() {
      this.controls = new TrackballControls(
        this.camera,
        this.renderer.domElement
      );
      this.controls.rotateSpeed = 1.0;
      this.controls.zoomSpeed = 1.2;
      this.controls.panSpeed = 0.8;
      this.controls.noZoom = false;
      this.controls.noPan = false;
      this.controls.staticMoving = true;
      this.controls.dynamicDampingFactor = 0.3;
      this.controls.keys = [65, 83, 68];
    },
    UPDATE_CONTROLS() {
      this.controls.update();
    },
    INITIALIZE_SCENE() {
      this.scene = new Scene();
      this.scene.background = new Color(0xcccccc);
      this.scene.fog = new FogExp2(0xcccccc, 0.002);
      var geometry = new CylinderBufferGeometry(0, 10, 30, 4, 1);
      var material = new MeshPhongMaterial({
        color: 0xffffff,
        flatShading: true,
      });
      for (var i = 0; i < 500; i++) {
        var mesh = new Mesh(geometry, material);
        mesh.position.x = (Math.random() - 0.5) * 1000;
        mesh.position.y = (Math.random() - 0.5) * 1000;
        mesh.position.z = (Math.random() - 0.5) * 1000;
        mesh.updateMatrix();
        mesh.matrixAutoUpdate = false;
        this.pyramids.push(mesh);
      }
      this.scene.add(...this.pyramids);

      // lights
      var lightA = new DirectionalLight(0xffffff);
      lightA.position.set(1, 1, 1);
      this.scene.add(lightA);
      var lightB = new DirectionalLight(0x002288);
      lightB.position.set(-1, -1, -1);
      this.scene.add(lightB);
      var lightC = new AmbientLight(0x222222);
      this.scene.add(lightC);

      // Axis Line 1
      var materialB = new LineBasicMaterial({ color: 0x0000ff });
      var geometryB = new Geometry();
      geometryB.vertices.push(new Vector3(0, 0, 0));
      geometryB.vertices.push(new Vector3(0, 1000, 0));
      var lineA = new Line(geometryB, materialB);
      this.axisLines.push(lineA);

      // Axis Line 2
      var materialC = new LineBasicMaterial({ color: 0x00ff00 });
      var geometryC = new Geometry();
      geometryC.vertices.push(new Vector3(0, 0, 0));
      geometryC.vertices.push(new Vector3(1000, 0, 0));
      var lineB = new Line(geometryC, materialC);
      this.axisLines.push(lineB);

      // Axis 3
      var materialD = new LineBasicMaterial({ color: 0xff0000 });
      var geometryD = new Geometry();
      geometryD.vertices.push(new Vector3(0, 0, 0));
      geometryD.vertices.push(new Vector3(0, 0, 1000));
      var lineC = new Line(geometryD, materialD);
      this.axisLines.push(lineC);

      this.scene.add(...this.axisLines);
    },
    RESIZE(width, height) {
      this.width = width;
      this.height = height;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
      this.controls.handleResize();
      this.renderer.render(this.scene, this.camera);
    },
    SET_CAMERA_POSITION(x, y, z) {
      if (this.camera) {
        this.camera.position.set(x, y, z);
      }
    },
    RESET_CAMERA_ROTATION() {
      if (this.camera) {
        this.camera.rotation.set(0, 0, 0);
        this.camera.quaternion.set(0, 0, 0, 1);
        this.camera.up.set(0, 1, 0);
        this.controls.target.set(0, 0, 0);
      }
    },
    HIDE_AXIS_LINES() {
      this.scene.remove(...this.axisLines);
      this.renderer.render(this.scene, this.camera);
    },
    SHOW_AXIS_LINES() {
      this.scene.add(...this.axisLines);
      this.renderer.render(this.scene, this.camera);
    },
    HIDE_PYRAMIDS() {
      this.scene.remove(...this.pyramids);
      this.renderer.render(this.scene, this.camera);
    },
    SHOW_PYRAMIDS() {
      this.scene.add(...this.pyramids);
      this.renderer.render(this.scene, this.camera);
    },
    INIT(width, height, el) {
      console.log(height);
      console.log(el);
      return new Promise((resolve) => {
        this.SET_VIEWPORT_SIZE(width, height);
        this.INITIALIZE_RENDERER(el);
        this.INITIALIZE_CAMERA();
        this.INITIALIZE_CONTROLS();
        this.INITIALIZE_SCENE();

        // Initial scene rendering
        this.renderer.render(this.scene, this.camera);

        // Add an event listener that will re-render
        // the scene when the controls are changed
        this.controls.addEventListener("change", () => {
          this.renderer.render(this.scene, this.camera);
        });

        resolve();
      });
    },
    ANIMATE(dispatch) {
      window.requestAnimationFrame(() => {
        dispatch("ANIMATE");
        this.controls.update();
      });
    },
  },
});
