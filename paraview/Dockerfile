FROM alpine:edge

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

RUN apk update && apk add wget && apk add tar

WORKDIR /app/paraView

RUN wget -O paraView.tar.gz 'https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.10&type=binary&os=Linux&downloadFile=ParaView-5.10.1-osmesa-MPI-Linux-Python3.9-x86_64.tar.gz'

RUN tar xvzf paraView.tar.gz

EXPOSE 55
ENTRYPOINT ["tail", "-f", "/dev/null"]