#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

source /home/cb76/cb761228/perf-oriented-dev/.venv/bin/activate

#RUN FILEGEN BEFORE
/home/cb76/cb761228/perf-oriented-dev/small_samples/build/filegen 1000 150 5120 10240

#WITH LOAD
#/home/cb76/cb761228/perf-oriented-dev/tools/load_generator/exec_with_workstation_heavy.sh "python /home/cb76/cb761228/perf-oriented-dev/automated_tester/experiment_generator.py --config ./filesearch.json"

#WITHOUT LOAD
python /home/cb76/cb761228/perf-oriented-dev/automated_tester/experiment_generator.py --config ./filesearch.json

rm -r /tmp/generated_cb761228/