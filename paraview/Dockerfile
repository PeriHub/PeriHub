FROM alpine:edge

RUN apk update && apk add wget && apk add tar

WORKDIR /app/paraView

RUN wget -O paraView.tar.gz 'https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.9&type=binary&os=Linux&downloadFile=ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz'

RUN tar xvzf paraView.tar.gz

# FROM ubuntu:20.04

# ENV DEBIAN_FRONTEND=noninteractive
# WORKDIR /

# RUN apt-get -yq update
# RUN apt-get -yq install openssh-server\
#                         git \
#                         cmake \
#                         build-essential \
#                         # libgl1-mesa-dev \
#                         # libxt-dev \
#                         # qt5-default \
#                         # libqt5x11extras5-dev \
#                         # libqt5help5 \
#                         # qttools5-dev \
#                         # qtxmlpatterns5-dev-tools \
#                         # libqt5svg5-dev \
#                         python3-dev \
#                         python3-numpy \
#                         # libopenmpi-dev \
#                         # libtbb-dev \
#                         ninja-build

# COPY read.sh read.sh

# RUN git clone https://gitlab.kitware.com/paraview/paraview.git; \
#     mkdir paraview_build; \
#     cd paraview; \
#     git checkout v5.9.1; \
#     git submodule update --init --recursive; \
#     cd ../paraview_build; \
#     cmake \
#     -GNinja \
#     -DPARAVIEW_BUILD_EDITION=CORE \
#     -DPARAVIEW_USE_QT=OFF \
#     -DPARAVIEW_USE_QTHELP=OFF \
#     -DPARAVIEW_USE_PYTHON=ON \
#     -DCMAKE_BUILD_TYPE=Release ../paraview; \
#     ninja

# RUN mkdir /var/run/sshd

# WORKDIR /app/
# EXPOSE 55
# CMD    ["/usr/sbin/sshd", "-D"]