import numpy as np
from support.xmlCreator  import XMLcreator

class ModelWriter(object):
    def __init__(self, filename = 'mesh'):
        
        self.filename = filename
        self.nsName   = 'ns_' + filename
    def writeNodeSets(self, model, nslist):
        for idx, k in enumerate(nslist):
            points = np.where(model['k'] == k)
            string = ''
            for pt in points[0]:
                string += str(int(pt)+1) + '\n'
            self.fileWriter(self.nsName + '_' + str(idx+1) + '.txt', string)

    def fileWriter(self, filename, string):
        fid = open(filename,'w')
        fid.write(string)
        fid.close()
    def writeMesh(self, model):    
        string = '# x y z block_id volume\n'
        for idx in range(0, len(model['x'])):
            string += str(model['x'][idx]) + " " + str(model['y'][idx])+ " " + "0" + " " + str(model['k'][idx]) + " " + str(model['vol'][idx]) + "\n"
        self.fileWriter(self.filename + '.txt', string)
        
    def createXML(self, bcDict, materialDict,blockDef,bondfilters):
        xl = XMLcreator(filename = self.filename, nsName = self.nsName, bc = bcDict,materialDict = materialDict, blockDef = blockDef, bondfilters = bondfilters)
        string = xl.createXML()
        self.fileWriter(self.filename + '.xml', string)
        
