#!/bin/bash -x

cur_dir=`pwd`
id=0
for x in /home/dean/workspace/LP/geolife/Data/*
do
    cd $x/Trajectory
    cp $id $cur_dir/userdata/$id
    echo $id
    let id=id+1
    cd $cur_dir
done
