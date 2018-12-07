#!/bin/bash
GNUGO="gnugo-3.8/interface/gnugo"

cd $(dirname $0)

if [ -e $GNUGO ]; then
    echo "gnugo already exists"
else
    wget http://ftp.gnu.org/gnu/gnugo/gnugo-3.8.tar.gz
    tar -xzf gnugo-3.8.tar.gz
    cd gnugo-3.8
    ./configure
    make
fi
