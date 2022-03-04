class YAMLcreator:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.material_dict = model_writer.material_dict
        self.damage_dict = model_writer.damage_dict
        self.compute_dict = model_writer.compute_dict
        self.output_dict = model_writer.output_dict
        self.solver_dict = model_writer.solver_dict
        self.block_def = block_def
        self.bondfilters = model_writer.bondfilters
        self.boundary_condition = model_writer.bc_dict
        self.ns_name = model_writer.ns_name
        self.ns_list = model_writer.ns_list
        self.two_d = model_writer.two_d

    @staticmethod
    def translate_xml_to_yaml(string):
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
                elif len(partString) != 1:
                    stringYAML += spaces[0] + partString[1] + ": \n"

        return stringYAML
