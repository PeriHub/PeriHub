import axios from 'axios'

import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import { Plotly } from 'vue-plotly'
import D3Network from 'vue-d3-network'
import "vue-d3-network/dist/vue-d3-network.css"
import NetworkTest from '../assets/NetworkTest.json'
// import journalIcon from '../assets/book.svg'

const journalIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!--! Font Awesome Pro 6.0.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M448 336v-288C448 21.49 426.5 0 400 0H96C42.98 0 0 42.98 0 96v320c0 53.02 42.98 96 96 96h320c17.67 0 32-14.33 32-31.1c0-11.72-6.607-21.52-16-27.1v-81.36C441.8 362.8 448 350.2 448 336zM143.1 128h192C344.8 128 352 135.2 352 144C352 152.8 344.8 160 336 160H143.1C135.2 160 128 152.8 128 144C128 135.2 135.2 128 143.1 128zM143.1 192h192C344.8 192 352 199.2 352 208C352 216.8 344.8 224 336 224H143.1C135.2 224 128 216.8 128 208C128 199.2 135.2 192 143.1 192zM384 448H96c-17.67 0-32-14.33-32-32c0-17.67 14.33-32 32-32h288V448z"/></svg>'

export default {
    name: 'PeriHub',
    components: {
      D3Network,
      Splitpanes,
      Pane,
      Plotly,
      // pdf
      // RemoteComponent
    },
    data () {
      return {
        nodes: [
        { id: 1, name: 'my awesome node 1', _size:40},
        { id: 2, name: 'my node 2'},
        { id: 3, name:'orange node', _color: 'orange' },
        { id: 4, _color: '#4466ff'},
        { id: 5, _width:10, _height:10 },
        { id: 6 },
        { id: 7 },
        { id: 8 },
        { id: 9 }
      ],
      links: [
        { sid: 1, tid: 2 },
        { sid: 2, tid: 8 },
        { sid: 3, tid: 4,  _svgAttrs:{'stroke-width':8,opacity:1},name:'custom link' },
        { sid: 4, tid: 5 },
        { sid: 5, tid: 6 },
        { sid: 7, tid: 8 },
        { sid: 5, tid: 8 },
        { sid: 3, tid: 8 },
        { sid: 7, tid: 9 }
      ],
      canvas:false,
      size:{ w:1200, h:1200},
      offset:{ x:0, y:0},
      force: 30000,
      fX: 0.5,
      fY: 0.5,
      fMb: true,
      fL: true,
      fC: false,
      nodeSize: 20,
      linkWidth: 4,
      nodeLabels: true,
      linkLabels: true,
      fontSize: 20,
      strLinks: false,
      resizeListener: true,
      noNodes: false,
      
      pinned: false,
      selected: {},
      linksSelected: {},
      nodeSym: null,
      markerSize: 4,
      showSelection: false,

      // Model
      keywordList: [
        {
          id: 1,
          name: 'Peridynamics',
          keywords: [
          {
            id: 1,
            value: 'Peridynamics'
          },
          {
            id: 2,
            value: 'peridynamics'
          }],
          weight: 3
        },
        {
          id: 2,
          name: 'Composite',
          keywords: [
          {
            id: 1,
            value: 'composite'
          },
          {
            id: 2,
            value: 'CFRP'
          }],
          weight: 10
        }],
        url: 'https://perihub-api.fa-services.intra.dlr.de/',
        snackbar: false,
        message: 'Messsages',
        authToken: '',
        plotRawData: '',
        plotLoading: false,
        plotData:[{
          name: 'Displacement',
          x: [1,2,3,4],
          y: [10,15,20,17],
          type:"scatter"},{
          name: 'Force',
          x: [1,2,3,4],
          y: [10,15,5,17],
          type:"scatter"}],
        plotLayout:{
          // title: 'this.model.modelNameSelected',
          showlegend: true,
          // margin: { t: 50 },
          hovermode: "compare",
          bargap: 0,
          xaxis: {
            showgrid: true,
            zeroline: true,
            color: "white"
          },
          yaxis: {
            showgrid: true,
            zeroline: true,
            color: "white"
          },
          xaxis2: {
            showgrid: false,
            zeroline: false
          },
          yaxis2: {
            showgrid: true,
            zeroline: false
          },
          plot_bgcolor: "#2D2D2D",
          paper_bgcolor: "#2D2D2D",
          font: {
            color: "white"
          },
          modebar: {
            color: "white"
            // color: "#6E6E6E"
          },
        },
        plotOptions:{
          scrollZoom: true,
          setBackground: 'black'
        },
        logInterval: null,
        statusInterval: null,
        monitorToggle: false,
        viewId: 0,
        panel: [0],
        rules: {
          required: value => !!value || value == 0 || 'Required',
          name: value => {
            const pattern = /^[A-Za-z0-9_]{1,15}/
            return pattern.test(value) || 'Invalid name'
          },
          posFloat: value => {
            const pattern = /^((?!0)|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/
            return pattern.test(value) || 'Invalid number'
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
    computed:{
      options(){
        return{
          canvas: this.canvas,
          size: this.size,
          offset: this.offset,
          force: this.force,
          forces:{
           Center: this.fC,
           X:this.fX,
           Y:this.fY,
           ManyBody:this.fMb,
           Link:this.fL,
          },
          nodeSize: this.nodeSize,
          linkWidth: this.linkWidth,
          nodeLabels: this.nodeLabels,
          linkLabels: this.linkLabels,
          fontSize: this.fontSize,
          strLinks: this.strLinks,
          resizeListener: this.resizeListener,
          noNodes: this.noNodes
        }
      }
    },
    filters: {
      number(value)
      {
        return value.toFixed(2)
      }
    },
    methods: {
      changeIcon(){
        for (let node of this.nodes){
          console.log(node)
          if (node.svgSym == 'journalIcon'){
            let newNode = Object.assign(node,{svgSym:journalIcon, svgIcon:null, svgObj:null})
            this.$set(this.nodes,node.index,newNode)
          }
        }
      },
      loadJsonFile(fr, files) {
        this.model.ownModel=false
        this.model.translated=false
        
        fr.onload = e => {
          const result = JSON.parse(e.target.result);
          for(var j = 0; j < Object.keys(result).length; j++) {
            var paramName = Object.keys(result)[j]
            Object.assign(this[paramName], result[paramName])
          }
        }
        fr.readAsText(files.item(0));
      },
      resetData() {

        for(var i = 0; i < Object.keys(NetworkTest).length; i++) {
          var paramName = Object.keys(NetworkTest)[i]
          this.$set(this, paramName, NetworkTest[paramName])
        }
        this.changeIcon()
      },
      screenshot() {
        this.$refs["net"].screenShot("Test", "#aa00bb", true, true);
      },
      screenShotDone (err) {
        // this.toaster = err || 'Saving Screenshot...'
        // let vm = this
        // window.setTimeout(() => {
        //   vm.toaster = null
        // }, 3000)
      },
      getNode(event, node) {
        console.log(node)

        this.selectedNodes.push(node)
        this.showSelected(event, node)
      },
      nodeClick (event, node) {
        if (this.pinned) {
          this.pinNode(node)
        }
        else{
          // is selected
          if (this.selected[node.id]) {
            this.unSelectNode(node.id)
            // is not selected
          } else {
            this.selectNode(node)
          }
          this.selectNodesLinks()
        }
        this.updateSelection()
      },
      linkClick (event, link) {
        console.log(link)
      },
      selectNode (node) {
        this.selected[node.id] = node
      },
      selectLink (link) {
        this.$set(this.linksSelected, link.id, link)
      },
      clearSelection () {
        this.selected = {}
        this.linksSelected = {}
      },
      selectNodesLinks () {
        for (let link of this.links) {
          // node is selected
          if (this.selected[link.sid] || this.selected[link.tid]) {
            this.selectLink(link)
            // node is not selected
          } else {
            this.unSelectLink(link.id)
          }
        }
      },
      unSelectNode (nodeId) {
        if (this.selected[nodeId]) {
          delete (this.selected[nodeId])
        }
        this.selectNodesLinks()
      },
      getName(nodeId) {
        console.log(this.selected[nodeId].name)
      },
      unSelectLink (linkId) {
        if (this.linksSelected[linkId]) {
          delete (this.linksSelected[linkId])
        }
      },
      updateSelection () {
        this.showSelection = (Object.keys(this.selected).length | Object.keys(this.linksSelected).length)
      },
      pinNode (node) {
        if (!node.pinned) {
          node.pinned = true
          node.fx = node.x
          node.fy = node.y
        } else {
          node.pinned = false
          node.fx = null
          node.fy = null
        }
        this.nodes[node.index] = node
      },
      showSelected(event, node) {
        this.nodes[node.index]._color='gray'
      },
      // lcb(link){
      //   link._svgAttrs = { 'marker-end': 'url(#m-end)',
      //                    'marker-start': 'url(#m-start)'}
      //   return link
      // },
      saveData() {
        const data = "{\"model\": " + JSON.stringify(this.model, null, 2)+",\n" +
                      "\"materials\": " + JSON.stringify(this.materials, null, 2)+",\n" +
                      "\"damages\": " + JSON.stringify(this.damages, null, 2)+",\n" +
                      "\"blocks\": " + JSON.stringify(this.blocks, null, 2)+",\n" +
                      "\"boundaryConditions\": " + JSON.stringify(this.boundaryConditions, null, 2)+",\n" +
                      "\"bondFilters\": " + JSON.stringify(this.bondFilters, null, 2)+",\n" +
                      "\"computes\": " + JSON.stringify(this.computes, null, 2)+",\n" +
                      "\"outputs\": " + JSON.stringify(this.outputs, null, 2)+",\n" +
                      "\"solver\": " + JSON.stringify(this.solver, null, 2) + "}";
        var fileURL = window.URL.createObjectURL(new Blob([data], {type: 'application/json'}));
        var fileLink = document.createElement('a');
        fileLink.href = fileURL;
        fileLink.setAttribute('download', this.model.modelNameSelected + '.json');
        document.body.appendChild(fileLink);
        fileLink.click();
      },
      readData() {
        this.$refs.fileInput.click()
      },
      uploadMesh() {
        this.$refs.multifileInput.click()
      },
      uploadSo() {
        this.$refs.multiSoInput.click()
      },
      onFilePicked (event) {
        const files = event.target.files
        const filetype = files[0].type
        if (files.length <= 0) {
          return false;
        }

        const fr = new FileReader();
        
        if(filetype=='application/json'){
          this.loadJsonFile(fr, files)
        }
        else if(files[0].name.includes('.yaml')){
          this.loadYamlModel(fr, files)
        }
        else if(filetype=='text/xml'){
          this.loadXmlModel(fr, files)
        }
        else if(filetype=='.peridigm'){
          this.loadPeridigmModel(fr, files)
        }
        else{
          this.loadFeModel(files)
        }
      },
      onMultiFilePicked (event) {
        const files = event.target.files
        // const filetype = files[0].type
        if (files.length <= 0) {
          return false;
        }

        this.modelLoading = true
        this.uploadfiles(files)
        
        this.viewPointData()
        this.modelLoading = false
        this.snackbar=true
      },
      async uploadfiles(files) {
        // this.snackbar=true
        // this.message = JSON.parse("{\"Job\": " + JSON.stringify(this.job)+"}")
        const formData = new FormData();
        for (var i = 0; i < files.length; i++){
          formData.append('files',files[i])
        }

        let headersList = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'multipart/form-data',
        'Authorization': this.authToken
        }

        let reqOptions = {
          url: this.url + "uploadfiles",
          params: {ModelName: this.model.modelNameSelected},
          data: formData,
          method: "POST",
          headers: headersList,
        }

        this.message = 'Files have been uploaded'
        await axios.request(reqOptions)
        .catch((error) => {
          // console.log(response)
          this.message = error
          return
        })
      },
      async cancelJob() {
        let headersList = {
        'Cache-Control': 'no-cache',
        'Authorization': this.authToken
        }

        let reqOptions = {
          url: this.url + "cancelJob",
          params: {ModelName: this.model.modelNameSelected,
                  Cluster: this.job.cluster,},
          method: "PUT",
          headers: headersList,
        }

        await axios.request(reqOptions).then(response => (this.message = response.data))
        this.snackbar=true
        this.monitorStatus(false)
      },
      monitorLogFile() {
        if(this.monitorToggle){
          // this.getLogFile()
          this.logInterval = setInterval(() => {
            // this.getLogFile()
          }, 30000)
        }
        else{
          clearInterval(this.logInterval)
        }
      },
      addKeyword() {
        const len = this.keywordList.length
        this.keywordList.push({
          id: len+1,
          name: "Keyword"+(len+1),
          keywords: []
        })
      },
      removeKeyword(index) {
        this.keywordList.splice(index, 1)
      },
      addKey(index) {
        const len = this.keywordList[index].keywords.length
        this.keywordList[index].keywords.push({
          id: len+1,
        })
        // for (const key in this.keywordList[index].keywords[len-1]) {
        //   if(key!='id' & key!='Name'){
        //     this.$set(this.keywordList[index].keywords[len], key, this.keywordList[index].keywords[len-1][key])
        //   }
        // }
      },
      removeKey(index,subindex) {
        this.keywordList[index].keywords.splice(subindex, 1)
      },
      getCurrentData() {
        this.getLocalStorage('panel');
      },
      getLocalStorage(name){
        if (localStorage.getItem(name)) 
            this[name] = JSON.parse(localStorage.getItem(name));
      },
      deleteCookies() {
        this.dialogDeleteCookies = false;
        this.$cookie.delete('darkMode')
        localStorage.removeItem('panel');
      },
      getAuthToken() {
        let reqOptions = {
          url: "https://perihub.fa-services.intra.dlr.de"
        }
        axios.request(reqOptions).then(response => (this.authToken = response.headers.authorization));
        // console.log(this.authToken);
      },
      openHidePanels() {
        if (this.panel.length==0){
          this.panel=[0,1,2,3,4,5,6,7]
        }
        else{
          this.panel=[]
        }
      },
    },
    beforeMount() {
      // console.log("beforeMount")
      if(process.env.VUE_APP_ROOT_API!=undefined)
      {
        this.url = process.env.VUE_APP_ROOT_API
        console.log("changed URL: " + process.env.VUE_APP_ROOT_API)
      }
      else
      {
        this.getAuthToken();
      }
    },
    mounted() {
      // console.log("mounted")
      this.getCurrentData()
      // this.getStatus()
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
      clearInterval(this.logInterval)
      clearInterval(this.statusInterval)
    },
    watch: {
      model: {
          handler() {
              // console.log('model changed!');
              localStorage.setItem('model', JSON.stringify(this.model));
          },
          deep: true,
      },
      panel: {
          handler() {
              // console.log('panel changed!');
              localStorage.setItem('panel', JSON.stringify(this.panel));
          },
          deep: true,
      },
    },
  }