#!/usr/bin/env bash

cd ~/Projects/pair-o-matic/
[ $(( `date +\%W` % 2 )) == 1 ] && python pair-o-matic.py