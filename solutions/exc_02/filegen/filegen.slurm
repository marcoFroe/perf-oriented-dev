#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

source /home/cb76/cb761228/perf-oriented-dev/.venv/bin/activate

#WITH LOAD
#/home/cb76/cb761228/perf-oriented-dev/tools/load_generator/exec_with_workstation_heavy.sh "python /home/cb76/cb761228/perf-oriented-dev/automated_tester/experiment_generator.py --config ./filegen.json"

#NO LOAD
python /home/cb76/cb761228/perf-oriented-dev/automated_tester/experiment_generator.py --config ./filegen.json