import csv
import sys
import os


def compute_miss_rates(csv_file):
    # Dictionary to store averages and variances for counter entries
    data = {}

    # Read the CSV file
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["column_name"] == "counter":
                event = row["event_name"]
                average = float(row["average"])
                variance = float(row["variance"])
                data[event] = (average, variance)

    # Compute miss rates and their variances
    miss_rates = {}
    for event in data:
        if event.endswith("-misses"):
            # Construct the corresponding access event name
            access_event = event.replace("-misses", "s")
            if access_event in data:
                avg_m, var_m = data[event]
                avg_a, var_a = data[access_event]
                if avg_a > 0:
                    miss_rate = avg_m / avg_a
                    # Variance of miss rate using propagation of error (assuming independence)
                    var_r = (1 / avg_a) ** 2 * var_m + (avg_m / avg_a**2) ** 2 * var_a
                    miss_rates[event] = (miss_rate, var_r)

    # Print the miss rates and their variances
    for event, (rate, var_r) in miss_rates.items():
        print(f"{event}: {rate:.6f} (variance: {var_r:.2e})")


if __name__ == "__main__":
    csv_file = sys.argv[1]
    csv_file = os.path.abspath(csv_file)
    compute_miss_rates(csv_file)
