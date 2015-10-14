#!/usr/bin/env bash

cd ~/cocolab/pair-o-matic/
[ $(( `date +\%W` % 2 )) == 1 ] && python pair-o-matic.py