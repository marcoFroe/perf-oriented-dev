#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

source /home/cb76/cb761228/perf-oriented-dev/.venv/bin/activate

python /home/cb76/cb761228/perf-oriented-dev/solutions/exc_09/src/experiment_exec.py --rw-mix-values 0.99 --output_file /home/cb76/cb761228/perf-oriented-dev/solutions/exc_09/output/results-099.csv