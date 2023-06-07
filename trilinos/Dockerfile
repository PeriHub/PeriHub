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

ADD https://github.com/Kitware/CMake/releases/download/v3.20.5/cmake-3.20.5-linux-x86_64.sh /cmake-3.20.5-Linux-x86_64.sh
RUN mkdir /opt/cmake
RUN sh /cmake-3.20.5-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN cmake --version

#Build Trilinos
RUN git clone https://github.com/trilinos/Trilinos.git trilinos; \
    # git checkout trilinos-release-13-1-0; \
    mkdir trilinos/build
ADD trilinosCmake.sh /trilinos/build/trilinosCmake.sh
RUN chmod +x /trilinos/build/trilinosCmake.sh
RUN cd trilinos/build; \
    ./trilinosCmake.sh; \
    make && make install; \
    cd ../..; \
    rm -rf trilinos