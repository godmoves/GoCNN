#!/bin/bash

cd thirdparty
wget http://ftp.gnu.org/gnu/gnugo/gnugo-3.8.tar.gz
tar -xzf gnugo-3.8.tar.gz
cd gnugo-3.8
./configure
make
cp ./interface/gnugo ../../
cd ../../
