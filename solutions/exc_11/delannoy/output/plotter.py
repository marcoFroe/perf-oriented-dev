import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("delannoy_combined_output.csv")

# Group by 'name' and 'config_size', then calculate mean and std of 'run_time'
grouped = (
    df.groupby(["name", "config_size"])["run_time"]
    .agg(["mean", "std"])
    .reset_index()
)

# Pivot the data for plotting
pivot_mean = grouped.pivot(index="config_size", columns="name", values="mean")
pivot_std = grouped.pivot(index="config_size", columns="name", values="std")

# Plot
plt.figure(figsize=(12, 6))
x = np.arange(len(pivot_mean.index))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

# Plot bars for each name
for name in pivot_mean.columns:
    offset = width * multiplier
    rects = plt.bar(
        x + offset,
        pivot_mean[name],
        width,
        yerr=pivot_std[name],
        label=name,
        capsize=5,
    )
    multiplier += 1

# Add labels, title, and legend
plt.xlabel("Config Size")
plt.ylabel("Run Time [ns] (log scale)")
plt.title("Run Time vs Config Size (with Error Bars)")
plt.xticks(x + width, pivot_mean.index)
plt.legend(title="Name", loc="upper right")
plt.grid(True, which="both", ls="--", axis="y")

plt.savefig(
    "run_time_vs_config_size_bar.png",
    dpi=200,
    bbox_inches="tight"
)