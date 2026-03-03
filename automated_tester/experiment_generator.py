# Implementation was mostly done by hand. Path related stuff was later reworked with the help of CoPilot.

import itertools
import json
import argparse
import shutil
import os

# base directory of this script (used to resolve relative defaults)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TIME_OUTPUT_FILE = "time-output.csv"
# default slurm template; make absolute based on script location so that
# running from any working directory still finds the file.
DEFAULT_SLURM_FILE = os.path.join(BASE_DIR, "baseline.slurm")


def generate_requested_executables(exp: dict) -> list[str]:
    """Generates a list of commands to execute based on the provided configuration. Commands include measurement tools and their respective metrics."""
    experiments = []
    tools = select_measurement_tool(exp)
    commands = generate_commands(exp)
    for tool in tools:
        for command in commands:
            experiments.append(f"{tool} {command}")
    redirected_exp = redirect_output(
        experiments, exp["outputDirectory"], exp["expName"]
    )
    experiments = redirected_exp
    return experiments


def generate_commands(config: dict) -> list[str]:
    """Generates a list of commands to execute based on the provided configuration."""
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
        commands.append(command)
    return commands


def select_measurement_tool(req_measures: dict) -> list[str]:
    """Selects the appropriate measurement tools based on the requested tool and metrics."""
    tools = []
    for measurement in req_measures["measurements"]:
        tool = measurement["tool"]
        metrics = measurement["metrics"]
        if tool == "time":
            tools.append(build_time_command(metrics))
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
    command += f'"{args}"'
    return command


def redirect_output(commands: list[str], output_dir: str, exp_name: str) -> list[str]:
    """Redirects the output of the measurement tools to the specified output directory. Keep the normal output of the executable on stdout."""
    redirected_commands = []
    for command in commands:
        # detect the time tool more robustly; it always starts with the absolute
        # path used in `build_time_command`.
        if command.strip().startswith("/usr/bin/time"):
            target = os.path.join(output_dir, f"{exp_name}_{TIME_OUTPUT_FILE}")
            redirected = command + f" 2> {target}"
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

    # Generate headers for each tool
    headers = {}
    for measurement in measurements:
        tool = measurement["tool"]
        metrics = measurement["metrics"]
        header = [exp_name] + param_names + metrics
        headers[tool] = ",".join(header)
    return headers


def generate_csv_files(experiment: dict):
    """Generates CSV files with appropriate headers for each measurement tool based on the experiment configuration."""

    headers = generate_csv_headers(experiment)
    output_dir = experiment["outputDirectory"]
    exp_name = experiment["expName"]
    for tool, header in headers.items():
        if tool == "time":
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{exp_name}_{TIME_OUTPUT_FILE}")
            with open(output_file, "w") as f:
                f.write(header + "\n")
        else:
            print(f'Tool "{tool}" is not supported for CSV generation.')


def main():
    parser = argparse.ArgumentParser(description="Generate experiment configuration")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the JSON configuration file containing experiment definitions.",
    )
    parser.add_argument(
        "--base_slurm",
        type=str,
        required=False,
        default=DEFAULT_SLURM_FILE,
        help="Path to the base SLURM script template.",
    )
    args = parser.parse_args()

    # make the config path absolute so that relative directories inside the
    # file can be resolved against the config's directory
    config_path = os.path.abspath(args.config)
    config_dir = os.path.dirname(config_path)

    with open(config_path, "r") as f:
        config = json.load(f)
        for exp in config:
            # resolve any relative paths in the experiment specification
            src_dir = exp.get("sourceDirectory", "")
            if not os.path.isabs(src_dir):
                src_dir = os.path.join(config_dir, src_dir)
            exp["sourceDirectory"] = src_dir

            # place outputDirectory inside sourceDirectory by default
            out_dir = exp.get("outputDirectory", "")
            if not os.path.isabs(out_dir):
                out_dir = os.path.join(src_dir, out_dir)
            exp["outputDirectory"] = out_dir

            # ensure directories exist before we try to write into them
            os.makedirs(src_dir, exist_ok=True)
            os.makedirs(out_dir, exist_ok=True)

            commands = generate_requested_executables(exp)

            exp_slurm = os.path.join(src_dir, f"{exp['expName']}.slurm")

            # copy base slurm file; raise a helpful error if the template cannot
            # be found
            base_slurm = args.base_slurm
            if not os.path.isabs(base_slurm):
                base_slurm = os.path.join(BASE_DIR, base_slurm)
            if not os.path.exists(base_slurm):
                raise FileNotFoundError(f"base slurm template not found: {base_slurm}")

            shutil.copy2(base_slurm, exp_slurm)

            # append generated commands to the slurm script
            with open(exp_slurm, "a") as f:
                f.write("\n# Generated commands\n")
                for _ in range(exp["repetitions"]):
                    for command in commands:
                        f.write(f"{command}\n")
            generate_csv_files(exp)


if __name__ == "__main__":
    main()
