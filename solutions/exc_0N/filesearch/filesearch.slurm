#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

source /home/cb76/cb761228/perf-oriented-dev/.venv/bin/activate
/home/cb76/cb761228/perf-oriented-dev/small_samples/build/filegen

python /home/cb76/cb761228/perf-oriented-dev/automated_tester/experiment_generator.py --config ./filesearch.json