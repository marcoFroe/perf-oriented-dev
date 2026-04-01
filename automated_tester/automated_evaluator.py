#!/usr/bin/env python3
"""
Program to compute statistics (average and variance) for numerical columns in CSV files.
Searches through all subdirectories for 'output' folders and processes CSV files found within.
Appends results as comments to the end of each CSV file and generates violin plots.
"""

import os
import sys
import csv
from pathlib import Path
from typing import List, Dict, Tuple
import statistics

# Optional plotting dependencies for violin plots
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def is_numeric(value: str) -> bool:
    """Check if a string value can be converted to a number."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_numeric_values(column_data: List[str]) -> Tuple[List[float], bool]:
    """
    Extract numeric values from a column.
    Returns tuple of (numeric_values, all_numeric).
    """
    numeric_values = []
    all_numeric = True

    for value in column_data:
        if value.strip():  # Skip empty values
            if is_numeric(value):
                numeric_values.append(float(value))
            else:
                all_numeric = False

    return numeric_values, all_numeric


def compute_statistics(
    csv_file_path: str,
) -> Dict[Tuple, Dict[str, Tuple[float, float]]]:
    """
    Compute average and variance for all numeric columns in a CSV file, grouped by config_* columns and event_name if present.
    Returns a dictionary mapping configuration tuples to dictionaries of column statistics.
    Format: {(config_val1, config_val2, ..., event_name_val): {column_name: (avg, var), ...}, ...}
    """
    statistics_dict = {}

    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

            # Collect all rows of data
            rows = list(reader)

            if not rows:
                return statistics_dict

            # Identify config columns and event_name column if present
            config_indices = [
                idx
                for idx, header in enumerate(headers)
                if header.startswith("config_") or header == "event_name"
            ]
            config_headers = [headers[idx] for idx in config_indices]

            # Group rows by configuration values and event_name if present
            config_groups = {}
            for row in rows:
                # Create configuration key from config column values and event_name if present
                config_key = tuple(
                    row[idx] if idx < len(row) else "" for idx in config_indices
                )
                if config_key not in config_groups:
                    config_groups[config_key] = []
                config_groups[config_key].append(row)

            # Process each configuration group
            for config_key, group_rows in config_groups.items():
                group_stats = {}

                # Process each column (except config columns)
                for col_idx, header in enumerate(headers):
                    # Skip config columns
                    if col_idx in config_indices:
                        continue

                    column_data = [
                        row[col_idx] if col_idx < len(row) else "" for row in group_rows
                    ]
                    numeric_values, all_numeric = get_numeric_values(column_data)

                    # Only compute statistics if all non-empty values are numeric
                    if all_numeric and numeric_values:
                        try:
                            avg = statistics.mean(numeric_values)
                            # Only compute variance if we have more than one value
                            if len(numeric_values) > 1:
                                var = statistics.variance(numeric_values)
                            else:
                                var = 0.0
                            group_stats[header] = (avg, var)
                        except Exception as e:
                            print(
                                f"Error computing statistics for column '{header}' in {csv_file_path}: {e}"
                            )

                if group_stats:
                    statistics_dict[config_key] = group_stats

            # Store config headers for later use
            statistics_dict["__config_headers__"] = config_headers

    except Exception as e:
        print(f"Error reading CSV file {csv_file_path}: {e}")

    return statistics_dict


def append_statistics_to_csv(csv_file_path: str, statistics_dict: Dict) -> None:
    """
    Append statistics as comments to the end of a CSV file.
    Format: # <column name>: <avg> [<variance>]
    Grouped by configuration values.
    """
    # Extract config headers
    config_headers = statistics_dict.pop("__config_headers__", [])

    if not statistics_dict:
        return

    try:
        with open(csv_file_path, "a", encoding="utf-8") as f:
            f.write("\n# Statistics computed by automated_evaluator.py\n")

            # Sort configuration keys for consistent output
            for config_key in sorted(statistics_dict.keys()):
                group_stats = statistics_dict[config_key]

                # Write configuration line
                if config_headers:
                    config_str = ", ".join(
                        f"{header}={value}"
                        for header, value in zip(config_headers, config_key)
                    )
                    f.write(f"# Configuration: {config_str}\n")

                # Write statistics for this configuration
                for column_name in sorted(group_stats.keys()):
                    avg, var = group_stats[column_name]
                    f.write(f"# {column_name}: {avg} [{var}]\n")
                f.write("#\n")
    except Exception as e:
        print(f"Error appending statistics to {csv_file_path}: {e}")


def has_evaluation_section(csv_file_path: str) -> bool:
    """
    Check if a CSV file already has an evaluation section at the end.
    Returns True if an evaluation section is found, False otherwise.
    """
    try:
        with open(csv_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Check if there are at least 2 lines and if the last non-empty line starts with '# Statistics'
            for line in reversed(lines):
                stripped = line.strip()
                if stripped.startswith(
                    "# Statistics computed by automated_evaluator.py"
                ):
                    return True
                if stripped and not stripped.startswith("#"):
                    return False
    except Exception as e:
        print(f"Error checking evaluation section in {csv_file_path}: {e}")
    return False


def process_output_folders(root_path: str = ".") -> None:
    """
    Walk through all subdirectories starting from root_path.
    Find 'output' folders and process all CSV files within them.
    """
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Check if current directory is named 'output'
        if os.path.basename(dirpath) == "output":
            print(f"Processing output folder: {dirpath}")

            # Process all CSV files in this output folder
            for filename in filenames:
                if filename.lower().endswith(".csv"):
                    csv_file_path = os.path.join(dirpath, filename)
                    if has_evaluation_section(csv_file_path):
                        continue
                    print(f"  Processing CSV file: {csv_file_path}")

                    # Compute statistics
                    stats = compute_statistics(csv_file_path)

                    # Append statistics to file
                    append_statistics_to_csv(csv_file_path, stats.copy())

                    # Count configuration groups (exclude metadata key)
                    num_groups = len(
                        [k for k in stats.keys() if k != "__config_headers__"]
                    )
                    if num_groups > 0:
                        print(
                            f"    Added statistics for {num_groups} configuration group(s)"
                        )
                    else:
                        print(f"    No numeric columns found")


def main():
    """Main entry point."""
    # Get the starting directory from command-line argument or use current directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."

    # Convert to absolute path
    root_dir = os.path.abspath(root_dir)

    # Verify the directory exists
    if not os.path.isdir(root_dir):
        print(f"Error: Directory '{root_dir}' does not exist.")
        sys.exit(1)

    print(f"Starting automated evaluation from: {root_dir}")
    print("-" * 60)

    process_output_folders(root_dir)

    print("-" * 60)
    print("Evaluation complete!")


if __name__ == "__main__":
    main()
