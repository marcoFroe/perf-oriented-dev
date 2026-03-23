#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

valgrind --tool=massif /home/cb76/cb761228/perf-oriented-dev/larger_samples/ssca2/build/ssca2 17