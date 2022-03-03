class YAMLcreator(object):
    def __init__(self, modelWriter, blockDef={}):
        self.filename = modelWriter.filename
        self.materialDict = modelWriter.materialDict
        self.damageDict = modelWriter.damageDict
        self.computeDict = modelWriter.computeDict
        self.outputDict = modelWriter.outputDict
        self.solverDict = modelWriter.solverDict
        self.blockDef = blockDef
        self.bondfilters = modelWriter.bondfilters
        self.bc = modelWriter.bcDict
        self.nsName = modelWriter.nsName
        self.nsList = modelWriter.nsList
        self.TwoD = modelWriter.TwoD

    def translateXMLtoYAML(self, string):
        stringYAML = "Peridigm:\n"
        splitString = string.split("\n")
        for spl in splitString:
            if "</ParameterList>" not in spl and "<ParameterList>" not in spl:
                partString = spl.split('"')
                spaces = spl.split("<")

                if len(partString) > 3:

                    if "string" in partString[3]:
                        tempString = '"' + partString[5] + '"'
                    else:
                        tempString = partString[5]
                    stringYAML += spaces[0] + partString[1] + ": " + tempString + "\n"
                else:
                    if len(partString) != 1:
                        stringYAML += spaces[0] + partString[1] + ": \n"

        return stringYAML
