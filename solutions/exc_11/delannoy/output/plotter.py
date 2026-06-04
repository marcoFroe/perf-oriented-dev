import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("delannoy_combined_output.csv")

# Group by 'name' and 'config_size', then average the 'run_time'
grouped = df.groupby(["name", "config_size"])["run_time"].mean().reset_index()

# Pivot the data for easier plotting
pivot_df = grouped.pivot(index="config_size", columns="name", values="run_time")

# Plot
plt.figure(figsize=(10, 6))
for name in pivot_df.columns:
    plt.plot(pivot_df.index, pivot_df[name], label=name, marker="o")

plt.xscale("linear")
plt.yscale("log")
plt.xlabel("Config Size")
plt.ylabel("Run Time [ns]")
plt.title("Run Time vs Config Size")
plt.legend(title="Runtime vs Problem size")
plt.grid(True, which="both", ls="--")

plt.savefig("run_time_vs_config_size.png", dpi=200, bbox_inches="tight")
