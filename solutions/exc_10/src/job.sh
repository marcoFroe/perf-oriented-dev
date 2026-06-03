#!/bin/bash
#SBATCH --job-name=bench-run
#SBATCH --time=00:30:00
#SBATCH --ntask=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=lva

python experiment_exec.py unrolled 1