#!/bin/bash
case $1 in 
"globalData") 
    ./paraView/ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit/bin/pvpython support/exodusReader/globalData.py $2 $3
    ;;
"image") 
    ./paraView/ParaView-5.9.1-osmesa-MPI-Linux-Python3.8-64bit/bin/pvpython support/exodusReader/imageLastStep.py $2 $3 $4
    ;;
esac