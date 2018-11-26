#!/usr/bin/env bash
# get script dir
cd $(dirname $0)
pwd

# create train/test folders
if [ ! -e train ]; then
    mkdir train 
    mkdir test
    # move data into ./train
    echo *.dat | xargs mv -t ./train
fi

# split some data into ./test
val=0
count=0
for file in ./train/*; do
    if ! ((val % 100)); then
        mv "$file" ./test
        echo "$file"
        let "count+=1"
    fi
    let "val+=1"
done
echo "move $count file(s) into ./test"
