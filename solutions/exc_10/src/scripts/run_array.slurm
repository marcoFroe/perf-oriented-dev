#!/bin/bash

#SBATCH --partition=lva
#SBATCH --output=%x-%j.log
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --exclusive

python ./experiment_exec.py array 0.5