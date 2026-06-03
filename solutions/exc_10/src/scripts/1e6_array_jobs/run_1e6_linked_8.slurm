#!/bin/bash

#SBATCH --job-name=bench-1e6-linked-8
#SBATCH --partition=lva
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --output=%x-%j.log
#SBATCH --error=%x-%j.err

set -euo pipefail

WORK_DIR="${SLURM_SUBMIT_DIR:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)}"
CSV_PATH="$WORK_DIR/one_million_linked_8.csv"

RW_MIX=1.0
NUM_ELEMENTS=1000000
ELEMENT_SIZE=8
LIST_TYPE=linked

if [[ ! -f "$CSV_PATH" ]]; then
    printf 'rw_mix,num_elements,element_size,list_type,allocation,iteration_type,num_operations\n' > "$CSV_PATH"
fi

for ALLOCATION in random linear; do
    for ITERATION_TYPE in random linear; do
        NUM_OPERATIONS=$(cd "$WORK_DIR" && ./benchmarker "$RW_MIX" "$NUM_ELEMENTS" "$ELEMENT_SIZE" "$LIST_TYPE" "$ALLOCATION" "$ITERATION_TYPE")
        printf '%s,%s,%s,%s,%s,%s,%s\n' \
            "$RW_MIX" \
            "$NUM_ELEMENTS" \
            "$ELEMENT_SIZE" \
            "$LIST_TYPE" \
            "$ALLOCATION" \
            "$ITERATION_TYPE" \
            "$NUM_OPERATIONS" >> "$CSV_PATH"
    done
done
