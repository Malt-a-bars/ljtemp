#!/bin/sh

set -e

export PYTHONPATH=../src:$PYTHONPATH
shopt -s nullglob
for f in ../src/*.py
do
  pydoc -w $f
done
