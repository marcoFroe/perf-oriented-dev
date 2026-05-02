#!/bin/bash

CSV_FILE="/home/marco/Documents/perf-oriented-dev/solutions/exc_07/task1/mimalloc_results.csv"

# Write CSV header
echo "Iteration,System_Time_Seconds,Real_Time_Seconds,Max_Memory_KB" > "$CSV_FILE"

# Execute the command 10 times
for i in {1..10}; do
    cd /home/marco/Documents/perf-oriented-dev/solutions/exc_07/task1/allscale_api/build
    ninja clean
    # Directly append the iteration and /usr/bin/time output to the CSV
    LD_PRELOAD=/home/marco/Documents/perf-oriented-dev/solutions/exc_07/task1/mimalloc/build/libmimalloc.so /usr/bin/time -f "$i,%S,%e,%M" ninja 2>> "$CSV_FILE" > /dev/null
done