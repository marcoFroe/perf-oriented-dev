import argparse
import csv
import math
import os
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter


BENCHMARK_SECONDS = 2.0
RESULTS_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "results")
PLOT_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "report", "figures")

LIST_ORDER = ["array", "tiered", "unrolled", "linked"]
LIST_LABEL = {
    "array": "Array",
    "tiered": "Tiered Array",
    "unrolled": "Unrolled LL",
    "linked": "Linked List",
}


def plain_number_formatter(value, _pos):
    # Format x-axis ticks as full plain numbers (e.g. 1000000 instead of 1e6).
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:g}"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate benchmark report plots for sheet 10."
    )
    parser.add_argument(
        "--results-dir",
        default=RESULTS_DIR_DEFAULT,
        help="Directory that contains benchmark CSV files.",
    )
    parser.add_argument(
        "--out-dir",
        default=PLOT_DIR_DEFAULT,
        help="Output directory for generated plots.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show plots interactively in addition to saving.",
    )
    return parser.parse_args()


def load_records(results_dir):
    records = []
    csv_files = sorted(
        os.path.join(results_dir, name)
        for name in os.listdir(results_dir)
        if name.endswith(".csv")
    )

    for csv_path in csv_files:
        with open(csv_path, newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rec = {
                    "rw_mix": float(row["rw_mix"]),
                    "num_elements": int(row["num_elements"]),
                    "element_size": int(row["element_size"]),
                    "list_type": row["list_type"],
                    "allocation": row["allocation"],
                    "iteration_type": row["iteration_type"],
                    "num_operations": int(row["num_operations"]),
                }
                rec["ops_per_sec"] = rec["num_operations"] / BENCHMARK_SECONDS
                rec["time_per_op_ns"] = (BENCHMARK_SECONDS / rec["num_operations"]) * 1e9
                rec["throughput_mb_s"] = (
                    rec["num_operations"] * rec["element_size"] / BENCHMARK_SECONDS / (1024.0 * 1024.0)
                )
                records.append(rec)

    return records


def filter_records(records, **criteria):
    out = []
    for rec in records:
        keep = True
        for key, value in criteria.items():
            if value is None:
                continue
            if isinstance(value, (list, tuple, set)):
                if rec[key] not in value:
                    keep = False
                    break
            else:
                if rec[key] != value:
                    keep = False
                    break
        if keep:
            out.append(rec)
    return out


def by_list(records):
    grouped = defaultdict(list)
    for rec in records:
        grouped[rec["list_type"]].append(rec)
    return grouped


def save(fig, out_dir, filename, show=False):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    print(f"Saved {path}")


def first_available_common_element_sizes(records, target_num_elements):
    # For plot 4 we want a num_elements setting that maximizes available size coverage.
    by_ne = defaultdict(list)
    for rec in records:
        by_ne[rec["num_elements"]].append(rec)

    if target_num_elements in by_ne:
        return target_num_elements

    # fallback: choose the num_elements value with most distinct element sizes across all list types
    best_ne = None
    best_score = -1
    for ne, rows in by_ne.items():
        size_set = {r["element_size"] for r in rows}
        if len(size_set) > best_score:
            best_score = len(size_set)
            best_ne = ne
    return best_ne


def plot1_traversal(records, out_dir, show=False):
    # Plot 1: Traversal performance, 8-byte elements, rw=1, linear iteration
    base = filter_records(
        records,
        element_size=8,
        rw_mix=1.0,
        iteration_type="linear",
        list_type=LIST_ORDER,
    )

    for allocation in ["linear", "random"]:
        subset = filter_records(base, allocation=allocation)
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        fig_ns, ax_ns = plt.subplots(figsize=(8.5, 5.2))

        grouped = by_list(subset)
        for lt in LIST_ORDER:
            rows = sorted(grouped.get(lt, []), key=lambda r: r["num_elements"])
            if not rows:
                continue
            x = [r["num_elements"] for r in rows]
            y = [r["throughput_mb_s"] for r in rows]
            y_ns = [r["time_per_op_ns"] for r in rows]
            ax.plot(x, y, marker="o", linewidth=2.2, label=LIST_LABEL[lt])
            ax_ns.plot(x, y_ns, marker="o", linewidth=2.2, label=LIST_LABEL[lt])

        ax.set_xscale("log")
        ax.set_xticks(sorted({r["num_elements"] for r in subset}))
        ax.get_xaxis().set_major_formatter(FuncFormatter(plain_number_formatter))
        ax.set_xlabel("Number of elements")
        ax.set_ylabel("Traversal throughput (MB/s)")
        ax.set_title(f"Plot 1: Traversal throughput ({allocation} allocation, 8B, rw=1)")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        save(fig, out_dir, f"plot1_traversal_{allocation}.png", show=show)

        ax_ns.set_xscale("log")
        ax_ns.set_xticks(sorted({r["num_elements"] for r in subset}))
        ax_ns.get_xaxis().set_major_formatter(FuncFormatter(plain_number_formatter))
        ax_ns.set_xlabel("Number of elements")
        ax_ns.set_ylabel("Traversal time per operation (ns)")
        ax_ns.set_title(f"Plot 1b: Traversal latency ({allocation} allocation, 8B, rw=1)")
        ax_ns.legend(loc="best")
        ax_ns.grid(True, alpha=0.3)
        fig_ns.tight_layout()

        save(fig_ns, out_dir, f"plot1_traversal_{allocation}_nsop.png", show=show)


def plot2_allocation_effect(records, out_dir, show=False):
    # Plot 2: Effect of allocation strategy at 100000 elements, 8B, rw=1, linear iteration
    subset = filter_records(
        records,
        num_elements=100000,
        element_size=8,
        rw_mix=1.0,
        iteration_type="linear",
        list_type=LIST_ORDER,
    )

    fig, ax = plt.subplots(figsize=(8.7, 5.4))

    allocations = ["linear", "random"]
    width = 0.36
    x_idx = list(range(len(LIST_ORDER)))

    for j, allocation in enumerate(allocations):
        values = []
        for lt in LIST_ORDER:
            rows = [r for r in subset if r["list_type"] == lt and r["allocation"] == allocation]
            values.append(rows[0]["time_per_op_ns"] if rows else math.nan)

        offset = (j - 0.5) * width
        x_positions = [x + offset for x in x_idx]
        ax.bar(x_positions, values, width=width, label=allocation.capitalize())

    ax.set_xticks(x_idx)
    ax.set_xticklabels([LIST_LABEL[lt] for lt in LIST_ORDER])
    ax.set_ylabel("Traversal time per operation (ns)")
    ax.set_title("Plot 2: Allocation strategy effect (100000 elements, 8B, rw=1)")
    ax.legend(loc="best")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    save(fig, out_dir, "plot2_allocation_effect.png", show=show)


def plot3_operation_mix(records, out_dir, show=False):
    # Plot 3: Operation mix sensitivity at 100000 elements, random allocation,
    # linear iteration for both 8B and 512B.
    mix_order = [1.0, 0.99, 0.9, 0.5]

    for element_size in [8, 512]:
        subset = filter_records(
            records,
            num_elements=100000,
            element_size=element_size,
            allocation="random",
            iteration_type="linear",
            rw_mix=mix_order,
            list_type=LIST_ORDER,
        )

        if not subset:
            print(f"Warning: Plot 3 skipped element_size={element_size} because no matching records were found.")
            continue

        fig, (ax_abs, ax_rel) = plt.subplots(1, 2, figsize=(13.2, 5.2), sharex=True)

        grouped = by_list(subset)

        for lt in LIST_ORDER:
            rows = grouped.get(lt, [])
            row_by_mix = {r["rw_mix"]: r for r in rows}
            x = [m for m in mix_order if m in row_by_mix]
            y = [row_by_mix[m]["ops_per_sec"] for m in x]
            if x:
                ax_abs.plot(x, y, marker="o", linewidth=2.2, label=LIST_LABEL[lt])

            if 1.0 in row_by_mix and row_by_mix[1.0]["ops_per_sec"] > 0:
                baseline = row_by_mix[1.0]["ops_per_sec"]
                y_rel = [row_by_mix[m]["ops_per_sec"] / baseline for m in x]
                if x:
                    ax_rel.plot(x, y_rel, marker="o", linewidth=2.2, label=LIST_LABEL[lt])

        ax_abs.set_xlabel("RW/ID ratio")
        ax_abs.set_ylabel("Operations per second")
        ax_abs.set_title("Plot 3a: Absolute ops/s")
        ax_abs.set_xticks(mix_order)
        ax_abs.invert_xaxis()
        ax_abs.legend(loc="best")
        ax_abs.grid(True, alpha=0.3)

        ax_rel.set_xlabel("RW/ID ratio")
        ax_rel.set_ylabel("Relative ops/s (normalized to rw=1.0)")
        ax_rel.set_title("Plot 3b: Sensitivity normalized")
        ax_rel.set_xticks(mix_order)
        ax_rel.invert_xaxis()
        ax_rel.axhline(1.0, color="black", linestyle="--", linewidth=1.2, alpha=0.6)
        ax_rel.grid(True, alpha=0.3)

        fig.suptitle(
            "Operation mix sensitivity "
            f"(100000 elements, random allocation, {element_size}B)"
        )
        fig.tight_layout()

        if element_size == 8:
            save(fig, out_dir, "plot3_operation_mix.png", show=show)
        save(fig, out_dir, f"plot3_operation_mix_{element_size}b.png", show=show)


def plot4_element_size_impact(records, out_dir, show=False):
    # Plot 4: Element size impact at rw in {1.0, 0.5}, favoring num_elements=1000.
    target_ne = 1000

    for rw_mix in [1.0, 0.5]:
        base = filter_records(
            records,
            rw_mix=rw_mix,
            iteration_type="linear",
            list_type=LIST_ORDER,
        )
        if not base:
            print(f"Warning: Plot 4 skipped rw_mix={rw_mix} because no matching records were found.")
            continue

        selected_ne = first_available_common_element_sizes(base, target_ne)
        subset = filter_records(base, num_elements=selected_ne)

        # Use random allocation to align with most cache-unfriendly scenario in other plots.
        subset = filter_records(subset, allocation="random")
        if not subset:
            print(
                f"Warning: Plot 4 skipped rw_mix={rw_mix} because no random-allocation rows were found "
                f"for num_elements={selected_ne}."
            )
            continue

        fig, ax = plt.subplots(figsize=(8.7, 5.4))

        grouped = by_list(subset)
        expected_sizes = sorted({r["element_size"] for r in base})
        missing_notes = []
        for lt in LIST_ORDER:
            rows = sorted(grouped.get(lt, []), key=lambda r: r["element_size"])
            if not rows:
                continue
            x = [r["element_size"] for r in rows]
            y = [r["ops_per_sec"] for r in rows]
            ax.plot(x, y, marker="o", linewidth=2.2, label=LIST_LABEL[lt])
            missing_sizes = [s for s in expected_sizes if s not in x]
            if missing_sizes:
                missing_notes.append(f"{LIST_LABEL[lt]} missing {len(missing_sizes)} size(s)")

        ax.set_xscale("log")
        ax.set_xticks(sorted({r["element_size"] for r in subset}))
        ax.get_xaxis().set_major_formatter(FuncFormatter(plain_number_formatter))
        ax.set_xlabel("Element size (bytes)")
        ax.set_ylabel("Operations per second")
        ax.set_title(
            "Plot 4: Element size impact "
            f"(num_elements={selected_ne}, random allocation, rw={rw_mix:g})"
        )
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        if missing_notes:
            ax.text(
                0.02,
                0.02,
                " | ".join(missing_notes),
                transform=ax.transAxes,
                fontsize=8,
                alpha=0.85,
                bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.7},
            )
        fig.tight_layout()

        if rw_mix == 1.0:
            save(fig, out_dir, "plot4_element_size_impact.png", show=show)
        save(fig, out_dir, f"plot4_element_size_impact_rw{rw_mix:g}.png", show=show)

        if selected_ne != target_ne:
            print(
                "Warning: Plot 4 fallback used num_elements="
                f"{selected_ne} because size coverage for {target_ne} is incomplete (rw_mix={rw_mix:g})."
            )


def write_plot5_unavailable_note(records, out_dir):
    # Plot 5 requests insert/delete-specific timing, which is not present in current CSV schema.
    os.makedirs(out_dir, exist_ok=True)
    note_path = os.path.join(out_dir, "plot5_scaling_unavailable.txt")

    with open(note_path, "w", encoding="ascii") as handle:
        handle.write("Plot 5 (Insert/Delete scaling) could not be generated.\n")
        handle.write("Reason: input CSVs do not contain an operation type column (insert/delete).\n")
        handle.write("Available fields are: rw_mix, num_elements, element_size, list_type, allocation, iteration_type, num_operations.\n")
        handle.write("\n")
        handle.write("To generate Plot 5, benchmark output must include one row per operation kind, e.g. op_type in {insert, delete}.\n")

    print(f"Wrote {note_path}")


def plot6_allocation_penalty_ratio(records, out_dir, show=False):
    # ratio > 1 means random allocation is slower than linear allocation
    subset = filter_records(
        records,
        element_size=8,
        rw_mix=1.0,
        iteration_type="linear",
        list_type=LIST_ORDER,
    )

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    for lt in LIST_ORDER:
        by_ne = defaultdict(dict)
        for rec in subset:
            if rec["list_type"] != lt:
                continue
            by_ne[rec["num_elements"]][rec["allocation"]] = rec["time_per_op_ns"]

        x_vals = []
        y_vals = []
        for ne in sorted(by_ne.keys()):
            pair = by_ne[ne]
            if "random" in pair and "linear" in pair and pair["linear"] > 0:
                x_vals.append(ne)
                y_vals.append(pair["random"] / pair["linear"])
        if x_vals:
            ax.plot(x_vals, y_vals, marker="o", linewidth=2.2, label=LIST_LABEL[lt])

    ax.set_xscale("log")
    ax.set_xticks(sorted({r["num_elements"] for r in subset}))
    ax.get_xaxis().set_major_formatter(FuncFormatter(plain_number_formatter))
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.set_xlabel("Number of elements")
    ax.set_ylabel("Random / Linear time per op")
    ax.set_title("Plot 6: Allocation penalty ratio (8B, rw=1)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    save(fig, out_dir, "plot6_allocation_penalty_ratio.png", show=show)


def plot7_speedup_vs_array(records, out_dir, show=False):
    # speedup = array_time / structure_time, so >1 means structure is faster than array
    base = filter_records(
        records,
        element_size=8,
        rw_mix=1.0,
        iteration_type="linear",
        list_type=LIST_ORDER,
    )

    for allocation in ["linear", "random"]:
        subset = filter_records(base, allocation=allocation)
        array_by_ne = {
            r["num_elements"]: r["time_per_op_ns"]
            for r in subset
            if r["list_type"] == "array"
        }

        fig, ax = plt.subplots(figsize=(8.8, 5.2))
        for lt in ["tiered", "unrolled", "linked"]:
            rows = sorted(
                [r for r in subset if r["list_type"] == lt and r["num_elements"] in array_by_ne],
                key=lambda r: r["num_elements"],
            )
            if not rows:
                continue
            x = [r["num_elements"] for r in rows]
            y = [array_by_ne[r["num_elements"]] / r["time_per_op_ns"] for r in rows]
            ax.plot(x, y, marker="o", linewidth=2.2, label=LIST_LABEL[lt])

        ax.set_xscale("log")
        ax.set_xticks(sorted({r["num_elements"] for r in subset}))
        ax.get_xaxis().set_major_formatter(FuncFormatter(plain_number_formatter))
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
        ax.set_xlabel("Number of elements")
        ax.set_ylabel("Speedup vs Array (array_time / structure_time)")
        ax.set_title(f"Plot 7: Speedup vs Array ({allocation} allocation, 8B, rw=1)")
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        save(fig, out_dir, f"plot7_speedup_vs_array_{allocation}.png", show=show)


def plot8_winner_map(records, out_dir, show=False):
    # winner = structure with lowest time/op for each (num_elements, rw_mix)
    base = filter_records(
        records,
        element_size=8,
        iteration_type="linear",
        list_type=LIST_ORDER,
        rw_mix=[1.0, 0.99, 0.9, 0.5],
    )

    rw_order = [1.0, 0.99, 0.9, 0.5]
    color_map = ListedColormap(["#d9d9d9", "#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"])

    for allocation in ["linear", "random"]:
        subset = filter_records(base, allocation=allocation)
        num_elements = sorted({r["num_elements"] for r in subset})

        matrix = []
        for ne in num_elements:
            row = []
            for rw in rw_order:
                candidates = [
                    r for r in subset
                    if r["num_elements"] == ne and r["rw_mix"] == rw and r["list_type"] in LIST_ORDER
                ]
                if not candidates:
                    row.append(0)  # missing
                else:
                    best = min(candidates, key=lambda r: r["time_per_op_ns"])
                    row.append(LIST_ORDER.index(best["list_type"]) + 1)
            matrix.append(row)

        fig, ax = plt.subplots(figsize=(7.8, 4.8))
        im = ax.imshow(matrix, cmap=color_map, aspect="auto", vmin=0, vmax=4)
        _ = im  # keep reference explicit for linters

        ax.set_xticks(range(len(rw_order)))
        ax.set_xticklabels([str(v) for v in rw_order])
        ax.set_yticks(range(len(num_elements)))
        ax.set_yticklabels([str(v) for v in num_elements])
        ax.set_xlabel("RW/ID ratio")
        ax.set_ylabel("Number of elements")
        ax.set_title(f"Plot 8: Winner map ({allocation} allocation, 8B, lower ns/op wins)")

        legend_handles = [Patch(facecolor="#d9d9d9", label="Missing")]
        legend_handles.extend(
            Patch(facecolor=color_map(i + 1), label=LIST_LABEL[lt])
            for i, lt in enumerate(LIST_ORDER)
        )
        ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0)

        fig.tight_layout()
        save(fig, out_dir, f"plot8_winner_map_{allocation}.png", show=show)


def main():
    args = parse_args()

    if not os.path.isdir(args.results_dir):
        raise SystemExit(f"Results directory not found: {args.results_dir}")

    records = load_records(args.results_dir)
    if not records:
        raise SystemExit("No benchmark records found.")

    plt.style.use("seaborn-v0_8-whitegrid")

    plot1_traversal(records, args.out_dir, show=args.show)
    plot2_allocation_effect(records, args.out_dir, show=args.show)
    plot3_operation_mix(records, args.out_dir, show=args.show)
    plot4_element_size_impact(records, args.out_dir, show=args.show)
    write_plot5_unavailable_note(records, args.out_dir)
    plot6_allocation_penalty_ratio(records, args.out_dir, show=args.show)
    plot7_speedup_vs_array(records, args.out_dir, show=args.show)
    plot8_winner_map(records, args.out_dir, show=args.show)


if __name__ == "__main__":
    main()
