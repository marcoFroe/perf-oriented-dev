#!/bin/bash

# Get the starting directory from argument, default to current directory
start_dir="${1:-.}"

# Find all .slurm files in subdirectories and execute sbatch on them
find "$start_dir" -type f -name "*.slurm" | while read -r slurm_file; do
    echo "Found .slurm file: $slurm_file"
    dir=$(dirname "$slurm_file")
    (cd "$dir" && sbatch "$(basename "$slurm_file")")
done