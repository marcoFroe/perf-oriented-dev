import json
import argparse

def generate_experiment_config(config:dict):
    pass

def select_measurement_tool(req_measures:dict)->list[str]:
    """Selects the appropriate measurement tools based on the requested tool and metrics."""
    tools = []
    for measurement in req_measures["measurements"]:
        tool = measurement["tool"]
        metrics = measurement["metrics"]
        if tool == "time":
            tools.append(build_time_command(metrics))
        else:
            print(f"Tool \"{tool}\" is not supported.")
            continue
    return tools

def build_time_command(req_measures:dict)->str:
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
    command += f"\"{args}\""
    return command

def main():
    parser = argparse.ArgumentParser(description="Generate experiment configuration")
    parser.add_argument("--config", type=str, required=True, help="Path to the YAML configuration file")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)


if __name__ == "__main__":
    test = {"measurements": [
            {
                "tool": "time",
                "metrics": [
                    "real",
                    "user",
                    "sys"
                ]
            },
            {
                "tool": "memory_profiler",
                "metrics": [
                    "memory_usage"
                ]
            }
        ]}

    print(select_measurement_tool(test))
