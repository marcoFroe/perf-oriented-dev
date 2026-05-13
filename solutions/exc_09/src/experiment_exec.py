import itertools
from typing import Dict, List


# Define num_operations based on num_elements
def get_num_operations(num_elements: int):
    if num_elements == 10:
        return 100
    elif num_elements == 1000:
        return 50
    else:
        return 5


def generate_experiment_settings(
    rw_mix_values: List,
    element_size_values: List,
    num_elements_values: List,
    list_type_values: List,
    allocation_values: List,
) -> List[Dict]:
    # Generate all combinations
    combinations = []
    for rw_mix in rw_mix_values:
        for element_size in element_size_values:
            for num_elements in num_elements_values:
                # Skip if both element_size and num_elements are max
                if element_size == 8000000 and num_elements == 10000000:
                    continue
                for list_type in list_type_values:
                    if list_type == "linked":
                        for allocation in allocation_values:
                            num_operations = get_num_operations(num_elements)
                            combinations.append(
                                {
                                    "rw_mix": rw_mix,
                                    "element_size": element_size,
                                    "num_elements": num_elements,
                                    "list_type": list_type,
                                    "allocation": allocation,
                                    "num_operations": num_operations * num_elements,
                                }
                            )
                    else:
                        num_operations = get_num_operations(num_elements)
                        combinations.append(
                            {
                                "rw_mix": rw_mix,
                                "element_size": element_size,
                                "num_elements": num_elements,
                                "list_type": list_type,
                                "num_operations": num_operations * num_elements,
                            }
                        )
    return combinations


import subprocess
import csv


def execute_command_and_get_runtime(command):
    """
    Executes the command and returns the runtime (integer) from stdout.
    Assumes the C program prints only the runtime as an integer to stdout.
    """
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        # Strip whitespace and convert to integer
        runtime = int(result.stdout.strip())
        return runtime
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Command failed or invalid output: {e}")
        return None


def run_experiments(executable_path, combinations, csv_file="results.csv"):
    """
    Runs all parameter combinations, executes the C program, and logs results to CSV.
    """
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "rw_mix",
                "element_size",
                "num_elements",
                "list_type",
                "allocation",
                "num_operations",
                "runtime",
            ],
        )
        writer.writeheader()

        for combo in combinations:
            # Build the command
            command = [
                executable_path,
                f"{combo['rw_mix']}",
                f"{combo['num_operations']}",
                f"{combo['num_elements']}",
                f"{combo['element_size']}",
                combo["list_type"],
            ]
            if combo["list_type"] == "linked":
                command.append(combo["allocation"])
            else:
                command.append("linear")

            # Execute and get runtime
            runtime = execute_command_and_get_runtime(command)
            if runtime is not None:
                combo["runtime"] = runtime
                writer.writerow(combo)
                print(f"Completed: {combo}")
            else:
                print(f"Failed for: {combo}")


if __name__ == "__main__":
    # Define the parameter values
    rw_mix_values = [1, 0.99, 0.99, 0.5]
    element_size_values = [8, 512, 8000000]
    num_elements_values = [10, 1000, 100000, 10000000]
    list_type_values = ["array", "linked"]

    # Only for linked lists
    allocation_values = ["random", "linear"]

    combinations = generate_experiment_settings(
        rw_mix_values,
        element_size_values,
        num_elements_values,
        list_type_values,
        allocation_values,
    )

    print(len(combinations))

    # run_experiments("./benchmarker", combinations)
