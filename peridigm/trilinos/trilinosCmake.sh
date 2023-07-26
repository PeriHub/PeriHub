#!/bin/bash

# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

rm -f CMakeCache.txt 

MPI_HOME=/usr
EXTRA_ARGS=$@

cmake -D CMAKE_INSTALL_PREFIX:PATH=/usr/local/trilinos/ \
  \
  -D MPI_BASE_DIR:PATH=/usr \
  -D CMAKE_CXX_FLAGS:STRING="-O2 -std=c++11 -pedantic -ftrapv -Wall -Wno-long-long" \
  \
  -D CMAKE_BUILD_TYPE:STRING=Release \
  -D CMAKE_Fortran_COMPILER:FILEPATH=/usr/bin/mpif90 \
  -D Trilinos_WARNINGS_AS_ERRORS_FLAGS:STRING="" \
  -D Trilinos_ENABLE_ALL_PACKAGES:BOOL=OFF \
  -D Trilinos_ENABLE_Teuchos:BOOL=ON \
  -D Trilinos_ENABLE_Shards:BOOL=ON \
  -D Trilinos_ENABLE_Sacado:BOOL=ON \
  -D Trilinos_ENABLE_Epetra:BOOL=ON \
  -D Trilinos_ENABLE_EpetraExt:BOOL=ON \
  -D Trilinos_ENABLE_Ifpack:BOOL=ON \
  -D Trilinos_ENABLE_AztecOO:BOOL=ON \
  -D Trilinos_ENABLE_Amesos:BOOL=ON \
  -D Trilinos_ENABLE_Anasazi:BOOL=ON \
  -D Trilinos_ENABLE_Belos:BOOL=ON \
  -D Trilinos_ENABLE_ML:BOOL=ON \
  -D Trilinos_ENABLE_Phalanx:BOOL=ON \
  -D Trilinos_ENABLE_Intrepid:BOOL=ON \
  -D Trilinos_ENABLE_NOX:BOOL=ON \
  -D Trilinos_ENABLE_Stratimikos:BOOL=ON \
  -D Trilinos_ENABLE_Thyra:BOOL=ON \
  -D Trilinos_ENABLE_Rythmos:BOOL=ON \
  -D Trilinos_ENABLE_MOOCHO:BOOL=ON \
  -D Trilinos_ENABLE_TriKota:BOOL=OFF \
  -D Trilinos_ENABLE_Stokhos:BOOL=ON \
  -D Trilinos_ENABLE_Zoltan:BOOL=ON \
  -D Trilinos_ENABLE_Piro:BOOL=ON \
  -D Trilinos_ENABLE_Teko:BOOL=ON \
  -D Trilinos_ENABLE_SEACASIoss:BOOL=ON \
  -D Trilinos_ENABLE_SEACAS:BOOL=ON \
  -D Trilinos_ENABLE_SEACASBlot:BOOL=OFF \
  -D Trilinos_ENABLE_Pamgen:BOOL=ON \
  -D Trilinos_ENABLE_EXAMPLES:BOOL=OFF \
  -D Trilinos_ENABLE_TESTS:BOOL=ON \
  -D TPL_ENABLE_Matio:BOOL=OFF \
  -D TPL_ENABLE_HDF5:BOOL=ON \
  -D TPL_ENABLE_X11=OFF \
  -D HDF5_INCLUDE_DIRS:PATH=/usr/local/hdf5/include \
  -D HDF5_LIBRARY_DIRS:PATH=/usr/local/hdf5/lib \
  -D TPL_ENABLE_Netcdf:BOOL=ON \
  -D Netcdf_INCLUDE_DIRS:PATH=/usr/local/netcdf/include \
  -D Netcdf_LIBRARY_DIRS:PATH=/usr/local/netcdf/lib \
  -D TPL_ENABLE_MPI:BOOL=ON \
  -D TPL_ENABLE_BLAS:BOOL=ON \
  -D TPL_ENABLE_LAPACK:BOOL=ON \
  -D TPL_ENABLE_Boost:BOOL=OFF \
  -D TPL_ENABLE_yaml-cpp:BOOL=ON \
  -D TPL_yaml-cpp_LIBRARIES:FILEPATH=/usr/lib/x86_64-linux-gnu/libyaml-cpp.so \
  -D TPL_yaml-cpp_INCLUDE_DIRS:PATH=/usr/include/yaml-cpp \
  -D CMAKE_VERBOSE_MAKEFILE:BOOL=OFF \
  -D Trilinos_VERBOSE_CONFIGURE:BOOL=OFF \
  -D BUILD_SHARED_LIBS=ON \
  -D Trilinos_SHOW_DEPRECATED_WARNINGS:BOOL=OFF \
  \
  $EXTRA_ARGS \
  ..