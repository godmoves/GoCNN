#!/bin/bash
PACHI="pachi-pachi-12.10-jowa/pachi"

cd $(dirname $0)

if [ -e $PACHI ]; then
    echo "pachi already exists"
else
  wget https://github.com/pasky/pachi/archive/pachi-12.10-jowa.tar.gz
  tar -xzf pachi-12.10-jowa.tar.gz
  cd pachi-pachi-12.10-jowa
  sed 's/DCNN=1/# DCNN=1/g' Makefile > Makefile.tmp1
  sed 's/.git\/HEAD .git\/index/ /g' Makefile.tmp1 > Makefile.tmp2
  mv Makefile.tmp2 Makefile
  rm Makefile.tmp1
  make
fi
