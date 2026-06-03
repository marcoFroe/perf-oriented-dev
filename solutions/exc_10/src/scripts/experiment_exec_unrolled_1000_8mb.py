import subprocess
import os
import csv


CSV_PATH = "unrolled_1000_8mb_results.csv"
BENCHMARK_ARGS = {
    "rw_mix": 1.0,
    "num_elements": 1000,
    "element_size": 8000000,
    "list_type": "unrolled",
    "allocation": "random",
    "iteration_type": "random",
}


def run_script_and_log(script_path: str, csv_path: str = CSV_PATH):
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode="a", newline="", buffering=1) as csvfile:
        fieldnames = [
            "rw_mix",
            "num_elements",
            "element_size",
            "list_type",
            "allocation",
            "iteration_type",
            "num_operations",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        args = [
            str(BENCHMARK_ARGS["rw_mix"]),
            str(BENCHMARK_ARGS["num_elements"]),
            str(BENCHMARK_ARGS["element_size"]),
            BENCHMARK_ARGS["list_type"],
            BENCHMARK_ARGS["allocation"],
            BENCHMARK_ARGS["iteration_type"],
        ]

        result = subprocess.run(
            [script_path] + args,
            capture_output=True,
            text=True,
            check=True,
        )

        combo_with_result = BENCHMARK_ARGS.copy()
        combo_with_result["num_operations"] = int(result.stdout.strip())

        writer.writerow(combo_with_result)
        csvfile.flush()

    print(f"Results logged to {csv_path}")


if __name__ == "__main__":
    run_script_and_log("./benchmarker")