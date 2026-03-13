# Implementation was mostly done by hand.
# CoPilot helped with making Path related stuff robust and the output parsing.

import itertools
import json
import argparse
import subprocess
import os

# base directory of this script (used to resolve relative defaults)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TIME_OUTPUT_FILE = "time-output.csv"
PERF_OUTPUT_FILE = "perf-output.csv"


def generate_requested_executables(exp: dict) -> list[dict]:
    """Generates a list of commands to execute based on the provided configuration. Commands include measurement tools and their respective metrics."""
    experiments = []
    tools = select_measurement_tool(exp)
    commands_and_params = generate_commands_with_params(exp)
    for tool in tools:
        for cmd_param in commands_and_params:
            command = cmd_param["command"]
            params = cmd_param["params"]
            experiments.append(
                {
                    "tool": tool["name"],
                    "command": f"{tool['command']} {command}",
                    "params": params,
                }
            )
    return experiments


def generate_commands_with_params(config: dict) -> list[dict]:
    """Generates a list of commands with their parameters based on the provided configuration."""
    commands = []
    executable = config["executable"]
    configurations = config["configurations"]
    lang = config["lang"]

    # Extract parameter names and their values
    params = []
    for param in configurations:
        name = param["name"]
        values = param["values"] if "values" in param else param["value"]
        params.append((name, values))

    # Generate all combinations of parameter values
    param_names = [p[0] for p in params]
    param_values = [p[1] for p in params]
    for values in itertools.product(*param_values):
        # Build the command string
        if lang.lower() == "c" or lang.lower() == "cpp":
            # if parameter name is not needed
            args = " ".join(f"{value}" for _, value in zip(param_names, values))
        else:
            # if the parameter name is needed
            args = " ".join(
                f"--{name} {value}" for name, value in zip(param_names, values)
            )
        command = f"{executable} {args}"
        commands.append({"command": command, "params": list(values)})
    return commands


def select_measurement_tool(req_measures: dict) -> list[dict]:
    """Selects the appropriate measurement tools based on the requested tool and metrics."""
    tools = []
    reps = req_measures["repetitions"]
    for measurement in req_measures["measurements"]:
        tool = measurement["tool"]
        metrics = measurement["metrics"]

        for _ in range(reps):
            if tool == "time":
                tools.append({"name": "time", "command": build_time_command(metrics)})

            elif tool == "perf":
                tools.append(
                    {
                        "name": "perf",
                        "command": build_perf_command(metrics),
                    }
                )
            else:
                print(f'Tool "{tool}" is not supported.')
                continue
    return tools


def build_time_command(req_measures: dict) -> str:
    """Builds the command for the /usr/bin/time tool based on the requested metrics."""
    command = "/usr/bin/time -f "
    args = ""

    for metric in req_measures:
        if metric == "real":
            args += "%e"
        elif metric == "user":
            args += "%U"
        elif metric == "sys":
            args += "%S"
        elif metric == "max_mem":
            args += "%M"
        else:
            continue
        args += ","

    args = args[:-1]  # Remove the trailing comma
    command += args
    return command


def build_perf_command(req_counters: dict) -> str:
    """
    Builds the requested perf stat command. Output is in CSV format to stdout.
    """
    counters = ",".join(req_counters)

    command = f"perf stat -x, -e {counters} --"
    return command


def redirect_output(commands: list[str], output_dir: str, exp_name: str) -> list[str]:
    """Redirects the output of the measurement tools to the specified output directory. Keep the normal output of the executable on stdout."""
    redirected_commands = []
    for command in commands:
        # detect the time tool more robustly; it always starts with the absolute
        # path used in `build_time_command`.
        if command.strip().startswith("/usr/bin/time"):
            target = os.path.join(output_dir, f"{exp_name}_{TIME_OUTPUT_FILE}")
            redirected = command + f" 2>> {target}"
        else:
            redirected = command
        redirected_commands.append(redirected)

    return redirected_commands


def generate_csv_headers(experiment: dict) -> dict[str, str]:
    """Generates CSV headers for the output files based on the experiment configuration."""
    exp_name = experiment["expName"]
    configurations = experiment["configurations"]
    measurements = experiment["measurements"]

    # Extract parameter names
    param_names = [config["name"] for config in configurations]
    # Add config_ to each param for later parsing
    param_names = ["config_" + param for param in param_names]

    # Generate headers for each tool
    headers = {}
    for measurement in measurements:
        tool = measurement["tool"]
        metrics = measurement["metrics"]
        if tool == "time":
            header = ["name"] + param_names + metrics
        elif tool == "perf":
            header = (
                ["name"]
                + param_names
                + ["value", "event", "count", "time_enabled", "time_running"]
            )
        else:
            continue
        headers[tool] = ",".join(header)
    return headers


def generate_csv_files(experiment: dict) -> dict[str, str]:
    """Generates CSV files with appropriate headers for each measurement tool based on the experiment configuration.
    Returns for each tool the generated file path.
    """

    headers = generate_csv_headers(experiment)
    output_dir = experiment["outputDirectory"]
    exp_name = experiment["expName"]
    gen_files = dict()
    file_name = ""

    for tool, header in headers.items():
        if tool == "time":
            file_name = TIME_OUTPUT_FILE
        elif tool == "perf":
            file_name = PERF_OUTPUT_FILE
        else:
            print(f'Tool "{tool}" is not supported for CSV generation.')
            continue

        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{exp_name}_{file_name}")
        gen_files[tool] = output_file
        with open(output_file, "w") as f:
            f.write(header + "\n")
    return gen_files


def adapt_paths(exp: dict, config_dir: str) -> dict:
    """
    Method adapts all paths to be absolute.
    """
    # resolve any relative paths in the experiment specification
    src_dir = exp.get("sourceDirectory", "")
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(config_dir, src_dir)
    src_dir = os.path.normpath(src_dir)
    exp["sourceDirectory"] = src_dir

    # place outputDirectory inside sourceDirectory by default
    out_dir = exp.get("outputDirectory", "")
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(src_dir, out_dir)
    out_dir = os.path.normpath(out_dir)
    exp["outputDirectory"] = out_dir

    # make executable path absolute
    executable = exp.get("executable", "")
    if executable and not os.path.isabs(executable):
        executable = os.path.join(config_dir, executable)
    executable = os.path.normpath(executable)
    exp["executable"] = executable

    return exp


def parse_input_arguments() -> argparse.Namespace:
    """
    Method to parse all required input parameters.
    """
    parser = argparse.ArgumentParser(description="Generate experiment configuration")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the JSON configuration file containing experiment definitions.",
    )
    parser.add_argument(
        "--not_execute",
        action="store_true",
        help="If set, commands get printed not executed.",
    )
    return parser.parse_args()


def parse_perf_output(raw_output: subprocess.CompletedProcess[str]) -> list[list[str]]:
    """
    Parses the return of the perf stat command.
    """
    # Parse stderr: each line is a CSV
    collected_output = []
    lines = raw_output.stderr.strip().split("\n")
    for line in lines:
        # removing meta comments added by perf
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split(",")
        if len(parts) >= 5:
            value, _, event, count, enabled, running = parts[:6]
            # remove the ":u" added by perf
            event = event[:-2]
            output = [value, event, count, enabled, running]
        else:
            print("Error while parsing perf output!")
            output = ["-1", "-1", "-1", "-1", "-1"]

        collected_output.append(output)
    return collected_output


def execute_commands(exp_name: str, commands: list[dict], output_files: dict) -> None:
    """
    Execute all commands and write the output in parsed format to the correct output files.
    """
    for cmd_dict in commands:
        tool = cmd_dict["tool"]
        command = cmd_dict["command"]
        params = cmd_dict["params"]

        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
        )

        # print output of program
        print(result.stdout, flush=True)

        # parse output accordingly
        if tool == "time":
            # Parse stderr: comma-separated values
            values = result.stderr.strip().split(",")
            row = [exp_name] + params + values
            with open(output_files["time"], "a") as f:
                f.write(",".join(str(x) for x in row) + "\n")
                f.flush()
        elif tool == "perf":
            parsed_output = parse_perf_output(result)
            for output_line in parsed_output:
                row = [exp_name] + params + output_line
                with open(output_files["perf"], "a") as f:
                    f.write(",".join(str(x) for x in row) + "\n")
                    f.flush()


def main() -> None:
    args = parse_input_arguments()

    # make the config path absolute so that relative directories inside the
    # file can be resolved against the config's directory
    config_path = os.path.abspath(args.config)
    config_dir = os.path.dirname(config_path)

    with open(config_path, "r") as f:
        config = json.load(f)
        for exp in config:
            exp = adapt_paths(exp, config_dir)

            src_dir = exp["sourceDirectory"]
            out_dir = exp["outputDirectory"]
            # ensure directories exist before we try to write into them
            os.makedirs(src_dir, exist_ok=True)
            os.makedirs(out_dir, exist_ok=True)

            commands = generate_requested_executables(exp)
            csv_paths = generate_csv_files(exp)

            if args.not_execute:
                for cmd_dict in commands:
                    print(cmd_dict["command"])
            else:
                execute_commands(exp["expName"], commands, csv_paths)


if __name__ == "__main__":
    main()
