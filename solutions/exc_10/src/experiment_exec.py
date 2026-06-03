import itertools
import subprocess
from typing import List, Dict
import os
import csv
import sys


def generate_combinations(
    rw_mix_values: List,
    element_size_values: List,
    num_element_values: List,
    list_type_values: List,
    allocation_values: List,
    iteration_type: List,
) -> List:
    # Create a list of all parameter sets
    parameter_sets = [
        rw_mix_values,
        element_size_values,
        num_element_values,
        list_type_values,
        allocation_values,
        iteration_type,
    ]

    # Generate all combinations
    combinations = list(itertools.product(*parameter_sets))

    # Convert each combination tuple to a dictionary with the appropriate keys
    keys = [
        "rw_mix",
        "element_size",
        "num_elements",
        "list_type",
        "allocation",
        "iteration_type",
    ]

    result = [dict(zip(keys, combo)) for combo in combinations]
    return result


def combi_remover(combinations: List):
    return [
        combo
        for combo in combinations
        if not (combo["element_size"] == 8000000 and combo["num_elements"] > 1000)
    ]


def run_script_and_log(
    combinations: List[Dict],
    script_path: str,
    csv_path: str = "results.csv",
    script_args_order: List[str] = [
        "rw_mix",
        "num_elements",
        "element_size",
        "list_type",
        "allocation",
        "iteration_type",
    ],
):
    # Check if CSV file exists to determine if header is needed
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode="a", newline="", buffering=1) as csvfile:
        fieldnames = script_args_order + ["num_operations"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for combo in combinations:
            args = [str(combo[key]) for key in script_args_order]

            result = subprocess.run(
                [script_path] + args,
                capture_output=True,
                text=True,
            )

            combo_with_result = combo.copy()
            combo_with_result["num_operations"] = int(result.stdout)

            writer.writerow(combo_with_result)
            csvfile.flush()

    print(f"Results logged to {csv_path}")


if __name__ == "__main__":
    element_size_values = [8, 512, 8000000]
    num_elementes_values = [10, 1000, 100000]
    allocation_values = ["random", "linear"]
    iteration_type = ["random", "linear"]

    if len(sys.argv) < 2:
        print("Usage: python script.py <list_type> <rw_mix>")
        sys.exit(1)

    list_type = sys.argv[1]
    rw_mix_values =[float(sys.argv[2])]

    combos = generate_combinations(
        rw_mix_values,
        element_size_values,
        num_elementes_values,
        [list_type],
        allocation_values,
        iteration_type,
    )

    cleaned_combos = combi_remover(combos)

    csv_path = str(list_type)+str(rw_mix_values) + "_results.csv"

    run_script_and_log(cleaned_combos, "./benchmarker", csv_path)
