FROM alpine:edge

RUN apk update && apk add wget && apk add tar

WORKDIR /app/paraView

RUN wget -O paraView.tar.gz 'https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.9&type=binary&os=Linux&downloadFile=ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit.tar.gz'

RUN tar xvzf paraView.tar.gz

EXPOSE 55
ENTRYPOINT ["tail", "-f", "/dev/null"]