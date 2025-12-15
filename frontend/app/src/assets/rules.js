// SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
//
// SPDX-License-Identifier: Apache-2.0

export default {
  required: (value) => {
    return !value?.length || 'Field is required';
    // return !!value || 'Field is required';
  },
  equation: (value) => {
    const pattern = /^([-+/*][\dxyztd]+(\.\d+)?)*/;
    return pattern.test(value) || 'Invalid equation';
  },
  name: (value) => {
    const pattern = /^[A-Za-z0-9_]{1,15}/;
    return pattern.test(value) || 'Invalid name';
  },
  posFloat: (value) => {
    if (value != null) {
      const pattern = /^((?!0)|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
      return pattern.test(value) || 'Invalid number';
    } else return true;
  },
  float: (value) => {
    if (value != null) {
      const pattern = /^((?!0)|[-]|(?=0+\.))(\d*\.)?\d+(e[-]\d+)?$|^0$/;
      return pattern.test(value) || 'Invalid number';
    } else return true;
  },
  int: (value) => {
    const pattern = /^[-]{0,1}(?<!\.)\d+(?!\.)$/;
    return pattern.test(value) || 'Invalid number';
  },
};
