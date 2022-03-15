FROM jthesse/netcdf

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ENV HOME /root

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