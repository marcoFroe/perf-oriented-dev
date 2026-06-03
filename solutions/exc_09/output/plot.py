import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read CSV data from file
# Replace with your actual filename
data = pd.read_csv(
    "/home/marco/Uni/01_PerformanceOrientedComputing/solutions/exc_09/output/results-combined.csv"
)


def plot_barplots_runtime_per_operation(df):
    # Ensure allocation column has consistent string values
    df["allocation"] = df["allocation"].fillna("None")

    # Compute runtime per operation
    df["runtime_per_operation"] = df["runtime"] / df["num_operations"]

    # Group by list_type and allocation
    grouped = df.groupby(["list_type", "allocation"])

    for (list_type, allocation), subset in grouped:

        fig, ax = plt.subplots(figsize=(10, 5))

        rw_mixes = sorted(subset["rw_mix"].unique())

        # Sort data consistently
        subset = subset.sort_values(["element_size", "num_elements", "rw_mix"])

        # Create x-axis labels
        base_subset = subset[subset["rw_mix"] == rw_mixes[0]].sort_values(
            ["element_size", "num_elements"]
        )

        labels = [
            f"size={row.element_size}\nN={row.num_elements}"
            for row in base_subset.itertuples()
        ]

        x = np.arange(len(labels))

        # Bar width
        width = 0.25

        # Plot one bar group per rw_mix
        for i, rw_mix in enumerate(rw_mixes):

            rw_subset = subset[subset["rw_mix"] == rw_mix].sort_values(
                ["element_size", "num_elements"]
            )

            ax.bar(
                x + i * width,
                rw_subset["runtime_per_operation"],
                width=width,
                label=f"rw_mix={rw_mix}",
            )

        # Center tick labels
        ax.set_xticks(x + width * (len(rw_mixes) - 1) / 2)
        ax.set_xticklabels(labels, rotation=45, ha="right")

        # Logarithmic y-axis
        ax.set_yscale("log")

        ax.set_ylabel("Runtime / Num Operations")
        ax.set_xlabel("Element Size and Number of Elements")

        ax.set_title(f"list_type={list_type}, allocation={allocation}")

        ax.legend()

        # No grid
        ax.grid(False)

        plt.tight_layout()

        # Save figure
        output_name = f"{list_type}_{allocation}_barplot.png"
        plt.savefig(output_name, dpi=300)

        plt.close()

        print(f"Saved: {output_name}")


def plot_runtime_per_operation_512(df):
    """
    Plot runtime per operation for element_size == 512
    for all combinations of list_type and allocation.
    """

    # Normalize allocation column
    df["allocation"] = df["allocation"].fillna("None")

    # Compute runtime per operation
    df["runtime_per_operation"] = df["runtime"] / df["num_operations"]

    # Filter for element_size == 512
    df_512 = df[df["element_size"] == 512]

    # Group by list_type and allocation
    grouped = df_512.groupby(["list_type", "allocation"])

    for (list_type, allocation), subset in grouped:

        fig, ax = plt.subplots(figsize=(8, 5))

        rw_mixes = sorted(subset["rw_mix"].unique())

        # Sort consistently
        subset = subset.sort_values(["num_elements", "rw_mix"])

        # X positions
        num_elements = sorted(subset["num_elements"].unique())
        x = np.arange(len(num_elements))

        # Bar width
        width = 0.25

        # Plot bars for each rw_mix
        for i, rw_mix in enumerate(rw_mixes):

            rw_subset = subset[subset["rw_mix"] == rw_mix].sort_values("num_elements")

            ax.bar(
                x + i * width,
                rw_subset["runtime_per_operation"],
                width=width,
                label=f"rw_mix={rw_mix}",
            )

        # Center tick labels
        ax.set_xticks(x + width * (len(rw_mixes) - 1) / 2)

        ax.set_xticklabels([f"N={n}" for n in num_elements])

        ax.set_ylabel("Runtime / Num Operations")
        ax.set_xlabel("Number of Elements")

        ax.set_title(
            f"element_size=512 | "
            f"list_type={list_type} | "
            f"allocation={allocation}"
        )

        ax.legend()

        # No grid
        ax.grid(False)

        plt.tight_layout()

        # Save plot
        output_name = f"runtime_per_op_512_" f"{list_type}_{allocation}.png"

        plt.savefig(output_name, dpi=300)

        plt.close()

        print(f"Saved: {output_name}")


plot_barplots_runtime_per_operation(data)
plot_runtime_per_operation_512(data)
