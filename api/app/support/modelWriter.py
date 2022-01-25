import numpy as np
import os
from support.xmlCreator  import XMLcreator
from support.yamlCreator  import YAMLcreator
import time
# from numba import jit

class ModelWriter(object):
    def __init__(self, modelClass):
        
        self.filename = modelClass.filename
        self.nsName = 'ns_' + modelClass.filename
        self.path = 'Output/'+ os.path.join(modelClass.username, modelClass.filename)
        self.bcDict = modelClass.bcDict
        self.damageDict = modelClass.damageDict
        self.materialDict = modelClass.materialDict
        self.computeDict = modelClass.computeDict
        self.outputDict = modelClass.outputDict
        self.solverDict = modelClass.solverDict
        self.bondfilters = modelClass.bondfilters
        self.DiscType = modelClass.DiscType
        self.TwoD = modelClass.TwoD
        if not os.path.exists('Output'):
            os.mkdir('Output')   
            
        numberOfNs = 0
        nodeSetIds = []
        for bc in self.bcDict:
            if(bc.blockId not in nodeSetIds):
                numberOfNs += 1
                nodeSetIds.append(bc.blockId)
        self.nsList = nodeSetIds

    def writeNodeSets(self, model):
        for idx, k in enumerate(self.nsList):
            points = np.where(model[:,3] == k)
            string = ''
            for pt in points[0]:
                string += str(int(pt)+1) + '\n'
            self.fileWriter(self.nsName + '_' + str(idx+1) + '.txt', string)

    def fileWriter(self, filename, string):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path+'/'+filename,'w') as f:
            f.write(string)

    def meshFileWriter(self, filename, string, meshArray, format):
        print('Write mesh file')
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path+'/'+filename,'w') as f:
            f.write(string)
            np.savetxt(f, meshArray, fmt=format, delimiter=' ')

    def writeMesh(self, model):   
        start_time = time.time() 
        string = '# x y z block_id volume\n'
        self.meshFileWriter(self.filename + '.txt', string, model, '%.18e %.18e %.18e %d %.18e')  
        print('Mesh written in ' + "%.2f seconds" % (time.time() - start_time))

    def writeMeshWithAngles(self, model):   
        start_time = time.time() 
        string = '# x y z block_id volume angle_x angle_y angle_z\n'  
        self.meshFileWriter(self.filename + '.txt', string, model, '%.18e %.18e %.18e %d %.18e %.18e %.18e %.18e')  
        print('Mesh written in ' + "%.2f seconds" % (time.time() - start_time))

    def createFile(self, blockDef):

            #string = yl.createYAML(string)
            
        #if self.solverDict['filetype'] == 'xml':
        xl = XMLcreator(self, blockDef = blockDef)
        string = xl.createXML()
        if self.solverDict.filetype == 'yaml':
            yl = YAMLcreator(self, blockDef = blockDef)
        
            string = yl.translateXMLtoYAML(string)
        #else:
        #    print('Not a supported filetye: ', self.solverDict['filetype'])   

        self.fileWriter(self.filename + '.' + self.solverDict.filetype, string)
            
        
