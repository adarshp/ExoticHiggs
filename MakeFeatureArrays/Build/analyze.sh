#!/bin/bash

source setup.sh

# Build input file list
ls -f ../../Events/Signals/Hc_HW/tautau_ll/14_TeV/$1/Events/run_*/*.lhco.gz > ../Input/$1

rm -rf ../Output/$1/*
./MadAnalysis5job ../Input/$1
