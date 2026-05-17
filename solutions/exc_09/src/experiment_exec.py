import itertools
from typing import Dict, List
import argparse


# Define num_operations based on num_elements
def get_num_operations(num_elements: int):
    if num_elements == 10:
        return 100
    elif num_elements == 1000:
        return 10
    else:
        return 2


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
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        print(f"  stderr: {e.stderr}")
        return None
    except ValueError as e:
        print(f"Invalid output format for command: {' '.join(command)}")
        print(f"  stdout: '{result.stdout.strip()}'")
        print(f"  ValueError: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error running command: {' '.join(command)}")
        print(f"  Error: {e}")
        return None


def run_experiments(
    executable_path, combinations, csv_file="results.csv", num_runs=1, run_id=1
):
    """
    Runs all parameter combinations, executes the C program, and logs results to CSV.

    Args:
        executable_path: Path to the C executable
        combinations: List of parameter combinations to test
        csv_file: Output CSV file path
        num_runs: Total number of runs for this batch (for logging)
        run_id: Current run number (1-indexed)
    """
    # Write header only on first run
    is_first_run = run_id == 1
    mode = "w" if is_first_run else "a"

    print(f"Opening CSV file: {csv_file} in mode '{mode}'")

    with open(csv_file, mode=mode, newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "run_id",
                "rw_mix",
                "element_size",
                "num_elements",
                "list_type",
                "allocation",
                "num_operations",
                "runtime",
            ],
        )
        if is_first_run:
            print("Writing CSV header...")
            writer.writeheader()
            file.flush()

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
                row = {
                    "run_id": run_id,
                    "rw_mix": combo["rw_mix"],
                    "element_size": combo["element_size"],
                    "num_elements": combo["num_elements"],
                    "list_type": combo["list_type"],
                    "allocation": combo.get("allocation", "None"),
                    "num_operations": combo["num_operations"],
                    "runtime": runtime,
                }
                writer.writerow(row)
                file.flush()
                print(
                    f"Run {run_id}/{num_runs} - Completed: {combo} - Runtime: {runtime}"
                )
            else:
                print(f"Run {run_id}/{num_runs} - Failed for: {combo}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run performance experiments with configurable rw_mix values"
    )
    parser.add_argument(
        "--rw-mix-values",
        type=float,
        nargs="+",
        default=[1, 0.99, 0.90, 0.5],
        help="List of rw_mix values to test (default: 1 0.99 0.90 0.5)",
    )
    parser.add_argument("--output_file", type=str, default="result.csv")
    args = parser.parse_args()

    # Define the parameter values
    rw_mix_values = args.rw_mix_values
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

    print(f"Total combinations: {len(combinations)}")

    # Number of runs per setting
    num_runs = 10
    executable_path = (
        "/home/cb76/cb761228/perf-oriented-dev/solutions/exc_09/src/benchmarker"
    )
    csv_file = args.output_file

    for run_id in range(1, num_runs + 1):
        print(f"\n=== Running experiment set {run_id}/{num_runs} ===")
        run_experiments(
            executable_path,
            combinations,
            csv_file=csv_file,
            num_runs=num_runs,
            run_id=run_id,
        )
        print(f"=== Completed run {run_id}/{num_runs} ===\n")
