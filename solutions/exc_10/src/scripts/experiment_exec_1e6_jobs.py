#!/usr/bin/env python3
"""Submit 1,000,000-element benchmarks as a Slurm array job.

The submit mode writes a small Slurm job script and submits it with `sbatch`.
Each array task runs exactly one benchmark combination, and only the sizes that
make sense for 1,000,000 elements are scheduled (8 and 512 bytes; 8,000,000 is
excluded).

The worker mode is invoked by Slurm for one array task and writes one CSV file
per benchmark combination, so there are no concurrent writes to the same file.

Use --rw-mix <value> to submit only one rw_mix at a time.
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from itertools import product
from typing import List, Sequence, Tuple


LIST_TYPES = ["array", "linked", "unrolled", "tiered"]
ELEMENT_SIZES = [8, 512]
NUM_ELEMENTS = 1_000_000
RW_MIXES = [1.0, 0.99, 0.9, 0.5]
ALLOCATIONS = ["random", "linear"]
ITERATION_TYPES = ["random", "linear"]


JobSpec = Tuple[float, str, int, int, str, str]


def build_jobs() -> List[JobSpec]:
    return list(product(RW_MIXES, LIST_TYPES, ELEMENT_SIZES, [NUM_ELEMENTS], ALLOCATIONS, ITERATION_TYPES))


def output_file_for_job(output_dir: str, task_id: int, job: JobSpec) -> str:
    rw_mix, list_type, element_size, num_elements, allocation, iteration_type = job
    return os.path.join(
        output_dir,
        "runs",
        f"task_{task_id:03d}",
        f"rw{rw_mix:g}_{list_type}_n{num_elements}_s{element_size}_alloc{allocation}_iter{iteration_type}.csv",
    )


def write_job_csv(csv_path: str, job: JobSpec, num_operations: int) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["rw_mix", "num_elements", "element_size", "list_type", "allocation", "iteration_type", "num_operations"],
        )
        writer.writeheader()
        rw_mix, list_type, element_size, num_elements, allocation, iteration_type = job
        writer.writerow(
            {
            "rw_mix": rw_mix,
                "num_elements": num_elements,
                "element_size": element_size,
                "list_type": list_type,
                "allocation": allocation,
                "iteration_type": iteration_type,
                "num_operations": num_operations,
            }
        )


def run_benchmark(script_dir: str, job: JobSpec) -> int:
    rw_mix, list_type, element_size, num_elements, allocation, iteration_type = job
    cmd = [
        os.path.join(script_dir, "benchmarker"),
        str(rw_mix),
        str(num_elements),
        str(element_size),
        list_type,
        allocation,
        iteration_type,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        raise RuntimeError(f"benchmarker failed for {cmd}: {stdout} {stderr}".strip())
    return int(result.stdout.strip())


def write_slurm_script(slurm_path: str, script_path: str, job_count: int, output_dir: str, partition: str, time_limit: str) -> None:
    os.makedirs(os.path.dirname(slurm_path), exist_ok=True)
    content = f"""#!/bin/bash
#SBATCH --job-name=bench-1e6
#SBATCH --partition={partition}
#SBATCH --time={time_limit}
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --array=0-{job_count - 1}
#SBATCH --output={os.path.join(output_dir, 'logs', '%x-%A_%a.log')}

python3 {script_path} --worker --task-id $SLURM_ARRAY_TASK_ID --output-dir {output_dir}
"""
    with open(slurm_path, "w", newline="") as handle:
        handle.write(content)


def submit_slurm_job(slurm_path: str) -> str:
    result = subprocess.run(["sbatch", slurm_path], capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        raise RuntimeError(f"sbatch failed for {slurm_path}: {stdout} {stderr}".strip())
    return result.stdout.strip()


def write_manifest(output_dir: str, jobs: Sequence[JobSpec]) -> str:
    manifest_path = os.path.join(output_dir, "manifest_1e6_jobs.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(manifest_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["task_id", "rw_mix", "num_elements", "element_size", "list_type", "allocation", "iteration_type", "output_file"],
        )
        writer.writeheader()
        for task_id, job in enumerate(jobs):
            rw_mix, list_type, element_size, num_elements, allocation, iteration_type = job
            writer.writerow(
                {
                    "task_id": task_id,
                    "rw_mix": rw_mix,
                    "num_elements": num_elements,
                    "element_size": element_size,
                    "list_type": list_type,
                    "allocation": allocation,
                    "iteration_type": iteration_type,
                    "output_file": output_file_for_job(output_dir, task_id, job),
                }
            )
    return manifest_path


def worker_mode(script_dir: str, output_dir: str, task_id: int) -> int:
    jobs = build_jobs()
    if task_id < 0 or task_id >= len(jobs):
        raise IndexError(f"task-id {task_id} is out of range for {len(jobs)} jobs")

    job = jobs[task_id]
    output_file = output_file_for_job(output_dir, task_id, job)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    print(f"Running task {task_id}: {job}", flush=True)
    num_operations = run_benchmark(script_dir, job)
    write_job_csv(output_file, job, num_operations)
    print(f"Wrote {output_file}", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit or run 1e6 benchmarks as Slurm jobs.")
    parser.add_argument("--submit", action="store_true", help="Write a Slurm array script and submit it with sbatch.")
    parser.add_argument("--worker", action="store_true", help="Run the Slurm worker for one array task.")
    parser.add_argument("--task-id", type=int, default=None, help="Array task index for worker mode.")
    parser.add_argument("--rw-mix", type=float, default=None, choices=RW_MIXES, help="Submit only one rw_mix value at a time.")
    parser.add_argument("--output-dir", default=None, help="Directory for outputs. Defaults to ../results/1e6_jobs.")
    parser.add_argument("--slurm-dir", default=None, help="Directory where generated .slurm files are written.")
    parser.add_argument("--partition", default="lva", help="Slurm partition to use when submitting.")
    parser.add_argument("--time", dest="time_limit", default="00:30:00", help="Slurm time limit for each array job.")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = args.output_dir or os.path.normpath(os.path.join(script_dir, os.pardir, "results", "1e6_jobs"))
    slurm_dir = args.slurm_dir or os.path.join(script_dir, "generated_slurm")

    jobs = build_jobs()
    if args.rw_mix is not None:
        jobs = [job for job in jobs if job[0] == args.rw_mix]
        if not jobs:
            raise SystemExit(f"No jobs matched rw_mix={args.rw_mix}")

    if args.worker:
        if args.task_id is None:
            raise SystemExit("--worker requires --task-id")
        return worker_mode(script_dir, output_dir, args.task_id)

    if not args.submit:
        parser.error("choose either --submit or --worker")

    os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
    os.makedirs(slurm_dir, exist_ok=True)
    manifest_path = write_manifest(output_dir, jobs)
    slurm_path = os.path.join(slurm_dir, "experiment_exec_1e6_jobs.slurm")
    write_slurm_script(slurm_path, os.path.abspath(__file__), len(jobs), os.path.abspath(output_dir), args.partition, args.time_limit)
    submission = submit_slurm_job(slurm_path)
    print(f"Manifest: {manifest_path}")
    print(f"Submitted: {submission}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
