FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /

RUN apt-get -yq update
RUN apt-get -yq install openssh-server\
                        git \
                        cmake \
                        build-essential \
                        libgl1-mesa-dev \
                        libxt-dev \
                        qt5-default \
                        libqt5x11extras5-dev \
                        libqt5help5 \
                        qttools5-dev \
                        qtxmlpatterns5-dev-tools \
                        libqt5svg5-dev \
                        python3-dev \
                        python3-numpy \
                        libopenmpi-dev \
                        libtbb-dev \
                        ninja-build

RUN git clone https://gitlab.kitware.com/paraview/paraview.git; \
    mkdir paraview_build; \
    cd paraview; \
    git checkout v5.9.1; \
    git submodule update --init --recursive; \
    cd ../paraview_build; \
    cmake -GNinja -DPARAVIEW_USE_PYTHON=ON -DPARAVIEW_USE_MPI=ON -DVTK_SMP_IMPLEMENTATION_TYPE=TBB -DCMAKE_BUILD_TYPE=Release ../paraview; \
    ninja

RUN mkdir /var/run/sshd

WORKDIR /app/

EXPOSE 55
CMD    ["/usr/sbin/sshd", "-D"]