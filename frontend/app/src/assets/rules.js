// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export default {
  rules: {
    required: (value) => !!value || value == 0 || "Required",
    name: (value) => {
      const pattern = /^[A-Za-z0-9_]{1,15}/;
      return pattern.test(value) || "Invalid name";
    },
    posFloat: (value) => {
      const pattern = /^((?!0)|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
      return pattern.test(value) || "Invalid number";
    },
    float: (value) => {
      if (value != null) {
        const pattern = /^((?!0)|[-]|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
        return pattern.test(value) || "Invalid number";
      } else return true;
    },
    int: (value) => {
      const pattern = /^[-]{0,1}(?<!\.)\d+(?!\.)$/;
      return pattern.test(value) || "Invalid number";
    },
  },
};
