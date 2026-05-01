#!/bin/bash

COMMAND="./malloctest 1 500 1000000 10 1000"
CSV_FILE="custom_results.csv"

# Write CSV header
echo "Iteration,System_Time_Seconds,Real_Time_Seconds,Max_Memory_KB" > "$CSV_FILE"

# Execute the command 10 times
for i in {1..10}; do
    # Directly append the iteration and /usr/bin/time output to the CSV
    LD_PRELOAD=./my_allocator.so /usr/bin/time -f "$i,%S,%e,%M" ./malloctest 1 500 1000000 10 1000 2>> "$CSV_FILE"
done