#!/bin/bash
case $1 in 
"globalData") 
    ./paraView/ParaView-5.10.1-osmesa-MPI-Linux-Python3.9-x86_64/bin/pvpython support/exodusReader/globalData.py $2 $3 $4
    ;;
"image") 
    ./paraView/ParaView-5.10.1-osmesa-MPI-Linux-Python3.9-x86_64/bin/pvpython support/exodusReader/imageLastStep.py $2 $3 $4 $5 $6 $7 $8 $9
    ;;
esac