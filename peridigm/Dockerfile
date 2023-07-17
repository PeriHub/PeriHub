FROM jthesse/trilinos

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ENV HOME /root

WORKDIR /

RUN apt-get -yq update
RUN apt-get -yq install git
RUN apt-get -yq install openmpi-bin
RUN apt-get -yq install openssh-server
RUN apt-get -yq install libboost1.55
RUN git clone https://github.com/PeriHub/Peridigm.git Peridigm

RUN mkdir /Peridigm/build

WORKDIR /Peridigm/build/
RUN cmake \
    -D CMAKE_BUILD_TYPE:STRING=Release \
    -D CMAKE_INSTALL_PREFIX:PATH=/usr/local/peridigm \
    -D CMAKE_CXX_FLAGS:STRING="-O2 -Wall -std=c++14 -pedantic -Wno-long-long -ftrapv -Wno-deprecated" \
    -D TRILINOS_DIR:PATH=/usr/local/trilinos \
    -D CMAKE_CXX_COMPILER:STRING="mpicxx" \
    -D USE_DAKOTA:BOOL=OFF \
    -D USER_LIBRARY_DIRS=/Peridigm/src/materials/umats \
    ..; \
    make && make install;

VOLUME /output
WORKDIR /output
ENV LD_LIBRARY_PATH /usr/local/netcdf/lib
ENV PATH /usr/local/peridigm/bin:$PATH
ENV PATH /usr/local/trilinos/bin:$PATH

# Allow mpirun as root, should only be used in container
ENV OMPI_ALLOW_RUN_AS_ROOT 1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM 1

RUN mkdir /var/run/sshd

RUN  echo 'root:root' | chpasswd
RUN sed -i'' -e's/^#PermitRootLogin prohibit-password$/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i'' -e's/^#PasswordAuthentication yes$/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i'' -e's/^#PermitEmptyPasswords no$/PermitEmptyPasswords yes/' /etc/ssh/sshd_config \
    && sed -i'' -e's/^UsePAM yes/UsePAM no/' /etc/ssh/sshd_config
RUN service ssh start

WORKDIR /app/

EXPOSE 22
CMD    ["/usr/sbin/sshd", "-D"]
