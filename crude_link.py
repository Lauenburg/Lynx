#!/usr/bin/env python

import logging
import subprocess
from logging.handlers import RotatingFileHandler

import click
import omegaconf
import termcolor
import tzlocal
from apscheduler.schedulers.blocking import BlockingScheduler


def load_config(config_file: str) -> omegaconf.dictconfig.DictConfig:
    """
    Load the configuration file.

    Args:
        config_file (str): The path to the configuration file.

    Returns:
        omegaconf.dictconfig.DictConfig: The configuration file.
    """
    # Load the configuration file.
    cfg = omegaconf.OmegaConf.load(config_file)

    # TODO: Validate the configuration file.
    # validate_config(cfg)

    return cfg


def build_command(step: dict) -> str:
    """
    Build the command to be executed by subprocess.call().

    Args:
        step (DictConfig): The step to build the command for.

    Returns:
        str: The command to be executed.
    """
    # If the config specifies arguments for the current step, parse them into a list of strings
    # such that they can be processed by subprocess.call().
    if "arguments" in dict(step).keys():
        arguments = " ".join([f"--{key} {value}" for key, value in step.arguments.items()])
    else:
        arguments = ""

    # Build the command
    command = "python " + step.script + " " + arguments
    return command


@click.command()
@click.option(
    "--config-file",
    "-c",
    default="conf/config.yaml",
    help="The path to the configuration file.",
)
@click.option("--log-file", "-l", default="crude_link.log", help="The path to the log file.")
@click.option(
    "--non-interactive",
    "-n",
    is_flag=True,
    default=False,
    help="Run the pipeline in non-interactive mode.",
)
@click.option(
    "--keep-running",
    "-s",
    is_flag=True,
    default=False,
    help="Stop the current run but keep scheduling new runs in accordance with the cron settings.",
)
def main(config_file: str, log_file: str, non_interactive: bool, keep_running: bool) -> int:
    """Schedule the pipeline to run either once or on a regular basis using cron.

    Args:
        config_file (str): The path to the configuration file.
        log_file (str): The path to the log file.
        non_interactive (bool): Run the pipeline in non-interactive mode.
        keep_running (bool): Stop the current run but keep scheduling new runs in accordance with the cron settings.
    """
    # load the config file
    cfg = load_config(config_file)

    # schedule the pipeline to run on a regular basis using cron if cron is specified in the config file
    # and no-interactive is set to True.
    if non_interactive and "cron" in cfg.keys():
        # Schedule the pipeline to run on a regular basis using cron.
        bsched = BlockingScheduler(timezone=str(tzlocal.get_localzone()))
        bsched.add_job(
            lambda: schedular(cfg, non_interactive, log_file, keep_running, bsched),
            "cron",
            **dict(cfg.cron),
        )
        bsched.start()
    else:
        # Run the pipeline once.
        schedular(cfg, non_interactive)


def schedular(
    cfg: omegaconf.dictconfig.DictConfig,
    non_interactive: bool = False,
    log_file: str = "crude_link.log",
    keep_running: bool = True,
    bsched: BlockingScheduler = None,
) -> int:
    """
    Process the configuration file and execute the pipeline steps in order. In interactive mode,
    if a step encounters an error, the user is given the option to retry or skip it.
    Opting to retry will prompt the scheduler to restart the step, while selecting to skip
    will prompt the scheduler to inquire if the user wants to restart the entire pipeline or exit.
    In non-interactive mode, the pipeline will exit if a step encounters an error.
    The process is logged to a file if the --no-interactive flag is set.

    Args:
        cfg (DictConfig): The configuration file.
        non_interactive (bool): Run the pipeline in non-interactive mode.
        log_file (str): The path to the log file. Only used when non-interaciive is set to True.
        keep_running (bool): Stop the current run but keep scheduling new runs in accordance with the cron settings.

    Returns:
        int: 0 if the pipeline completes successfully, 1 if the user exits the pipeline.
    """

    # Set up logging if the --no-interactive flag is set.
    if non_interactive:
        handler = RotatingFileHandler(log_file, mode="w", maxBytes=2 * 1024 * 1024, backupCount=3, delay=False)
        handler.setLevel(logging.DEBUG)

        # Define the log message format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%a, %d %b %Y %H:%M:%S")
        handler.setFormatter(formatter)

        # Set up the logger
        logger = logging.getLogger(log_file)
        logger.setLevel(logging.DEBUG)

        # Add the handler to the logger
        logger.addHandler(handler)

    # Iterate through the pipeline steps and execute them in order.
    pipeline_steps = cfg.steps
    for i, step in enumerate(pipeline_steps):
        # Build the command to be executed.
        command = build_command(step)

        while True:
            # Print the step name and the script name to be executed.
            if non_interactive:
                logger.info(f"Processing Step {i+1}: {step.script}...")
            else:
                print(termcolor.colored(f"Processing Step {i+1}: {step.script}...", "yellow"))

            # Execute the step.
            try:
                # Default the return code to 0.
                return_code = 0

                if non_interactive:
                    logger.info("-" * 20 + " Output " + "-" * 20)
                else:
                    print("-" * 20 + " Output " + "-" * 20)

                # Execute the step and capture the output.
                if non_interactive:
                    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    logger.info("\n" + output.decode("utf-8").rstrip())
                else:
                    subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)

                if non_interactive:
                    logger.info("-" * 20 + "--------" + "-" * 20)
                else:
                    print("-" * 20 + "--------" + "-" * 20)

            except subprocess.CalledProcessError as e:
                # If the step fails, print the error and set the return code to the error code.
                if non_interactive:
                    logger.error(e.output.decode("utf-8").rstrip())
                    logger.info("-" * 20 + "--------" + "-" * 20)
                    logger.error(f"Step {i+1} ({step.script}) failed with error: {e}.")
                else:
                    print("-" * 20 + "--------" + "-" * 20)
                    print(termcolor.colored(f"Step {i+1} ({step.script}) failed with error: {e}.", "red"))

                # Update the return code
                return_code = e.returncode

            # Check the return code
            if return_code != 0 and non_interactive:
                # If the --no-interactive flag is set, exit the pipeline.
                if not keep_running and bsched is not None:
                    bsched.shutdown(wait=False)
                return 1
            elif return_code != 0:
                # If the return code is not 0, the step failed. Prompt the user to retry or skip the step.
                response = input(termcolor.colored("Do you want to rerun this step? (y/n)", "blue"))

                # If the user selects to retry, restart the step.
                if response.lower() == "y":
                    print("Restarting step...")
                else:
                    response = input(
                        termcolor.colored(
                            "Do you want to rerun the whole pipeline from the beginning? (y/n)",
                            "blue",
                        )
                    )
                    # If the user selects to restart the pipeline, restart the pipeline.
                    if response.lower() == "y":
                        print(termcolor.colored("Restarting pipeline...", "yellow"))
                        schedular(cfg)
                        return 0
                    else:
                        print(termcolor.colored("Exiting...", "red"))
                        return 1

            # If the return code is 0, the step completed successfully.
            else:
                if non_interactive:
                    logger.info(f"Step {i+1} ({step.script}) completed successfully.")
                else:
                    print(
                        termcolor.colored(
                            f"Step {i+1} ({step.script}) completed successfully.",
                            "green",
                        )
                    )
                break


if __name__ == "__main__":
    main()
