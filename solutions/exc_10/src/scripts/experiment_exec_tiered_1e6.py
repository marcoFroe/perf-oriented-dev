#!/usr/bin/env python3
"""Run benchmarker for `tiered` with num_elements=1_000_000 across allocation/iteration combos.
Writes results to `sheet_10/results/tiered_1e6_results.csv` and does not overwrite other files.
"""
import subprocess
import csv
import os
import sys

def main():
    rw_mix = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    element_size_values = [8, 512, 8000000]
    num_element_values = [1000000]
    # skip huge element size for very large counts
    allocation_values = ["random", "linear"]
    iteration_types = ["random", "linear"]

    out_dir = os.path.join(os.path.dirname(__file__), os.pardir, 'results')
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, 'tiered_1e6_results.csv')

    file_exists = os.path.isfile(csv_path)
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['rw_mix','num_elements','element_size','list_type','allocation','iteration_type','num_operations']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        for element_size in element_size_values:
            for num_elements in num_element_values:
                # don't run 8,000,000-byte elements with more than 1000 elements
                if element_size == 8000000 and num_elements > 1000:
                    print(f"Skipping element_size={element_size} with num_elements={num_elements}")
                    continue
                for allocation in allocation_values:
                    for iteration_type in iteration_types:
                        cmd = ['./benchmarker', str(rw_mix), str(num_elements), str(element_size), 'tiered', allocation, iteration_type]
                        print('Running:', ' '.join(cmd))
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        num_ops = int(res.stdout.strip())
                        writer.writerow({
                            'rw_mix': rw_mix,
                            'num_elements': num_elements,
                            'element_size': element_size,
                            'list_type': 'tiered',
                            'allocation': allocation,
                            'iteration_type': iteration_type,
                            'num_operations': num_ops,
                        })

    print(f'Results appended to {csv_path}')

if __name__ == '__main__':
    main()
