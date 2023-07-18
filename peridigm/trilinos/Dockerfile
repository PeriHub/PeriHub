# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0
#
# SPDX-FileCopyrightText: 2023 Trilinos Project <https://trilinos.github.io/license.html>
#
# SPDX-License-Identifier: BSD-3-Clause

FROM perihub/netcdf

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ENV HOME /root

#Intel_mkl
RUN wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB \
    | gpg --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
RUN apt update
RUN apt -y install intel-oneapi-mkl
RUN echo -e "source /opt/intel/oneapi/mkl/latest/env/vars.sh" >> ~/.bashrc

RUN apt-get -yq install g++ \ 
    gfortran \
    python \ 
    libblas-dev \
    liblapack-dev \
    libboost-dev \
    git \
    libyaml-cpp-dev

RUN apt-get -yq cmake
# ADD https://github.com/Kitware/CMake/releases/download/v3.20.5/cmake-3.20.5-linux-x86_64.sh /cmake-3.20.5-Linux-x86_64.sh
# RUN mkdir /opt/cmake
# RUN sh /cmake-3.20.5-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
# RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN cmake --version

#Build Trilinos
RUN git clone https://github.com/trilinos/Trilinos.git trilinos; \
    cd trilinos; \
    git checkout trilinos-release-13-2-0; \
    mkdir build; \
    cd ..
ADD trilinosCmake.sh /trilinos/build/trilinosCmake.sh
# RUN chmod +x /trilinos/build/trilinosCmake.sh
RUN cd /trilinos/build; \
    chmod +x trilinosCmake.sh; \
    # ./trilinosCmake.sh; \
    bash trilinosCmake.sh; \
    make -j 8 && make install; \
    cd ../..; \
    rm -rf trilinos