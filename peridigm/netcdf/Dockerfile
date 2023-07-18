# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

FROM ubuntu:20.04

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME /root

RUN apt-get update
RUN apt-get -yq install gcc \
    build-essential \
    wget \
    bzip2 \
    tar \
    zlib1g-dev \
    m4 \
    libopenmpi-dev \
    file \
    libcurl4-openssl-dev

#Build HDF5
RUN wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.0/src/hdf5-1.12.0.tar.bz2; \
    tar xjvf hdf5-1.12.0.tar.bz2; \
    cd hdf5-1.12.0; \
    ./configure --prefix=/usr/local/hdf5 --enable-parallel; \
    make; \
    make install; \
    cd ..; \
    rm -rf hdf5-1.12.0 hdf5-1.12.0.tar.bz2 

#Build netcdf
RUN wget https://github.com/Unidata/netcdf-c/archive/v4.8.0.tar.gz; \
    tar xzvf v4.8.0.tar.gz
ADD largefiles.patch netcdf-c-4.8.0/largefiles.patch
RUN cd netcdf-c-4.8.0; \
    patch -p1 < largefiles.patch; \
    ./configure --prefix=/usr/local/netcdf --disable-netcdf-4 --disable-dap \ 
    CC=mpicc \
    LDFLAGS=-L/usr/local/hdf5/lib \
    CFLAGS=-I/usr/local/hdf5/include; \
    make; \
    make install;\
    cd ..;\
    rm -rf netcdf-c-4.8.0 v4.8.0.tar.gz
