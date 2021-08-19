import numpy as np
import os
from support.xmlCreator  import XMLcreator
from support.yamlCreator  import YAMLcreator

class ModelWriter(object):
    def __init__(self, modelClass):
        
        self.filename = modelClass.filename
        self.nsName = 'ns_' + modelClass.filename
        self.path = 'Output/'+ modelClass.filename
        self.filetype = modelClass.filetype
        self.finalTime = modelClass.finalTime
        self.frequency = modelClass.frequency
        self.solvertype = modelClass.solvertype
        self.bcDict = modelClass.bcDict
        self.damageDict = modelClass.damageDict
        self.materialDict = modelClass.materialDict
        self.computeDict = modelClass.computeDict
        self.outputDict = modelClass.outputDict
        self.bondfilters = modelClass.bondfilters
        self.nsList = modelClass.nsList
        self.TwoD = modelClass.TwoD
        self.onlyTension = modelClass.onlyTension
        self.initStep = modelClass.initStep
        if not os.path.exists('Output'):
            os.mkdir('Output')   
    def writeNodeSets(self, model):
        for idx, k in enumerate(self.nsList):
            points = np.where(model['k'] == k)
            string = ''
            for pt in points[0]:
                string += str(int(pt)+1) + '\n'
            self.fileWriter(self.nsName + '_' + str(idx+1) + '.txt', string)

    def fileWriter(self, filename, string):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        fid = open(self.path+'/'+filename,'w')
        fid.write(string)
        fid.close()
    def writeMesh(self, model):    
        string = '# x y z block_id volume\n'
        for idx in range(0, len(model['x'])):
            string += str(model['x'][idx]) + " " + str(model['y'][idx])+ " " + str(model['z'][idx]) + " " + str(int(model['k'][idx])) + " " + str(model['vol'][idx]) + "\n"
        self.fileWriter(self.filename + '.txt', string)
    def writeMeshWithAngles(self, model):    
        string = '# x y z block_id volume angle_x angle_y angle_z\n'
        for idx in range(0, len(model['x'])):
            string += str(model['x'][idx]) + " " + str(model['y'][idx])+ " " + str(model['z'][idx]) + " " + str(int(model['k'][idx])) + " " + str(model['vol'][idx]) + " " + str(model['angle_x'][idx]) +" " + str(model['angle_y'][idx]) +" " + str(model['angle_z'][idx]) +"\n"
            # if idx < 20:
            #     print(string)
        self.fileWriter(self.filename + '.txt', string)       
    def createFile(self, blockDef):
        
        if self.filetype == 'yaml':
            yl = YAMLcreator(self, blockDef = blockDef)
            string = yl.createYAML()
            self.fileWriter(self.filename + '.yaml', string)
            
        elif self.filetype == 'xml':
            xl = XMLcreator(self, blockDef = blockDef)
            string = xl.createXML()
        else:
            print('Not a supported filetye: ', self.filetype)    
        self.fileWriter(self.filename + '.' + self.filetype, string)
            
        
