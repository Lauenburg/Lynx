import subprocess
from dataclasses import dataclass
from typing import Dict

import hydra


@hydra.main(config_path="conf", config_name="config", version_base="1.1")
def scheduler(cfg):
    pipeline_steps = cfg.steps
    for i, step in enumerate(pipeline_steps):
        print(dict(step))
        if "arguments" in dict(step).keys():
            arguments = ",".join([f"--{key}, {value}" for key, value in step.arguments.items()]).split(",")
        else:
            arguments = []
        result = subprocess.call(["python " + step.script] + arguments, shell=True)
        if result != 0:
            print(f"Step {i+1} ({step.script}) failed with error code {result}.")
            response = input("Do you want to restart this step? (y/n)")
            if response.lower() == "y":
                print("Restarting step...")
                result = subprocess.call(["python " + step.script] + arguments, shell=True)
            else:
                print("Skipping failed step...")
                response = input("Do you want to rerun the whole pipeline from the beginning? (y/n)")
                if response.lower() == "y":
                    print("Restarting pipeline...")
                    scheduler(cfg)
                else:
                    print("Exiting...")
                    return 1
        else:
            print(f"Step {i+1} ({step.script}) completed successfully.")


if __name__ == "__main__":
    scheduler()
