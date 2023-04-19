import os
import subprocess

import hydra
import termcolor


def real_path(path: str) -> str:
    """
    Check if the path is absolute or relative and return the absolute path.

    Args:
        path (str): The path to check.

    Returns:
        str: The absolute path.
    """
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
    return path


def build_command(step: dict) -> str:
    """
    Build the command to be executed by subprocess.call().

    Args:
        step (DictConfig): The step to build the command for.

    Returns:
        str: The command to be executed.
    """
    # If the step has arguments, parse them into a list of strings to be further processed by subprocess.call().
    if "arguments" in dict(step).keys():
        arguments = " ".join(
            [
                f"--{key} {real_path(value)}" if isinstance(value, str) and "/" in value else f"--{key} {value}"
                for key, value in step.arguments.items()
            ]
        )
    else:
        arguments = ""

    # Build the command
    command = "python " + real_path(step.script) + " " + arguments
    return command


@hydra.main(config_path="conf", config_name="config", version_base="1.1")
def scheduler(cfg):
    """
    Process the configuration file and execute the pipeline steps in order. If a step encounters an error, the user is given
    the option to retry or skip it. Opting to retry will prompt the scheduler to restart the step, while selecting to skip
    will prompt the scheduler to inquire if the user wants to restart the entire pipeline or exit.

    Args:
        cfg (DictConfig): The configuration file.

    Returns:
        int: 0 if the pipeline completes successfully, 1 if the user exits the pipeline.
    """

    # Iterate through the pipeline steps and execute them in order.
    pipeline_steps = cfg.steps
    for i, step in enumerate(pipeline_steps):
        # Build the command to be executed.
        command = build_command(step)

        while True:
            # Execute the step.
            print(termcolor.colored(f"Processing Step {i+1}: {step.script}...", "yellow"))
            result = subprocess.call(command, shell=True)

            # Check the return code. If the return code is non-zero, prompt the user to retry or skip the step.
            if result != 0:
                print(termcolor.colored(f"Step {i+1} ({step.script}) failed with error code {result}.", "red"))
                response = input(termcolor.colored("Do you want to rerun this step? (y/n)", "blue"))

                if response.lower() == "y":
                    print("Restarting step...")
                else:
                    response = input(
                        termcolor.colored("Do you want to rerun the whole pipeline from the beginning? (y/n)", "blue")
                    )
                    if response.lower() == "y":
                        print(termcolor.colored("Restarting pipeline...", "yellow"))
                        scheduler(cfg)
                    else:
                        print(termcolor.colored("Exiting...", "red"))
                        return 1
            else:
                print(termcolor.colored(f"Step {i+1} ({step.script}) completed successfully.", "green"))
                break


if __name__ == "__main__":
    scheduler()
