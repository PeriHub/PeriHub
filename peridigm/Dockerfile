FROM trilinos 

ARG GITLAB_USER
ENV GITLAB_USER $GITLAB_USER
ARG GITLAB_TOKEN
ENV GITLAB_TOKEN $GITLAB_TOKEN

ENV HOME /root

WORKDIR /

RUN apt-get -yq update
RUN apt-get -yq install git
RUN apt-get -yq install openmpi-bin
RUN apt-get -yq install openssh-server
RUN apt-get -yq install libboost1.55
RUN git clone https://${GITLAB_USER}:${GITLAB_TOKEN}@gitlab.dlr.de/AG-SATT/peridigmDev.git peridigm

# #Build Peridigm
# RUN mkdir peridigm
# WORKDIR /peridigm
# ADD src src
# ADD test test
# ADD scripts scripts
# ADD examples examples 
# ADD CMakeLists.txt .
RUN mkdir /peridigm/build

WORKDIR /peridigm/build/
RUN cmake \
    -D CMAKE_BUILD_TYPE:STRING=Release \
    -D CMAKE_INSTALL_PREFIX:PATH=/usr/local/peridigm \
    -D CMAKE_CXX_FLAGS:STRING="-O2 -Wall -std=c++14 -pedantic -Wno-long-long -ftrapv -Wno-deprecated" \
    -D TRILINOS_DIR:PATH=/usr/local/trilinos \
    -D CMAKE_CXX_COMPILER:STRING="mpicxx" \
    -D USE_DAKOTA:BOOL=OFF \
    ..; \
    make && make install; \
    cd ..; \
    rm -rf peridigm

VOLUME /output
WORKDIR /output
ENV LD_LIBRARY_PATH /usr/local/netcdf/lib
ENV PATH /usr/local/peridigm/bin:$PATH
ENV PATH /usr/local/trilinos/bin:$PATH

RUN mkdir /var/run/sshd

RUN  echo 'root:root' | chpasswd
RUN service ssh start

WORKDIR /app/

EXPOSE 22
CMD    ["/usr/sbin/sshd", "-D"]
