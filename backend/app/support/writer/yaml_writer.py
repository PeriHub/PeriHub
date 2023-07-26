# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0


class YAMLcreator:
    @staticmethod
    def translate_xml_to_yaml(string):
        string_yaml = "Peridigm:\n"
        split_string = string.split("\n")
        for spl in split_string:
            if "</ParameterList>" not in spl and "<ParameterList>" not in spl:
                if "<Parameter" not in spl and ">" in spl:
                    string_yaml += spl.split('"')[0] + "\n"
                elif "<Parameter" not in spl:
                    string_yaml += spl + "\n"
                else:
                    part_string = spl.split('"')
                    spaces = spl.split("<")

                    if len(part_string) > 3:
                        if "string" in part_string[3]:
                            if ">" in part_string[5]:
                                temp_string = ">"
                            else:
                                temp_string = '"' + part_string[5] + '"'
                        else:
                            temp_string = part_string[5]
                        string_yaml += spaces[0] + part_string[1] + ": " + temp_string + "\n"
                    elif len(part_string) != 1:
                        string_yaml += spaces[0] + part_string[1] + ": \n"

        return string_yaml
