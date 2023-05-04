#!/usr/bin/env python

import logging
import subprocess
from logging.handlers import RotatingFileHandler

import click
import fire
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
    # Build the command
    arguments = ""
    if "arguments" in step.keys():
        for arg in step.arguments:
            logging.info(arg)
            arguments += arg + " "

    return "python " + step.script + " " + arguments


def setup_logger(log_file: str) -> logging.Logger:
    """Set up the logger using a rotating file handler.

    Args:
        log_file (str): The path to the log file.

    Returns:
        logging.Logger: The logger.
    """
    handler = RotatingFileHandler(log_file, mode="w", maxBytes=2 * 1024 * 1024, backupCount=3, delay=False)
    handler.setLevel(logging.INFO)

    # Define the log message format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%a, %d %b %Y %H:%M:%S")
    handler.setFormatter(formatter)

    # Set up the logger
    logger = logging.getLogger(log_file)
    logger.setLevel(logging.INFO)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


def scheduler(
    config_file: str = "conf/config.yaml",
    log_file: str = None,
    non_interactive: bool = False,
    keep_running: bool = False,
) -> None:
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
            lambda: linker(cfg, log_file, non_interactive, keep_running, bsched),
            "cron",
            **dict(cfg.cron),
        )
        bsched.start()
    else:
        # Run the pipeline once.
        linker(cfg, log_file, non_interactive)


def linker(
    cfg: omegaconf.dictconfig.DictConfig,
    log_file: str = None,
    non_interactive: bool = False,
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
        log_file (str): The path to the log file. Only used when non-interactive is set to True.
        keep_running (bool): Stop the current run but keep scheduling new runs in accordance with the cron settings.
        bsched (BlockingScheduler): The scheduler. Only used when keep-running is set to True.

    Returns:
        int: 0 if the pipeline completes successfully, 1 if the user exits the pipeline or an error is thrown.
    """

    # Set up logging if the --no-interactive flag is set and log_file is not none.
    if log_file:
        logger = setup_logger(log_file)

    # Iterate through the pipeline steps and execute them in order.
    pipeline_steps = cfg.steps
    for i, step in enumerate(pipeline_steps):
        # Build the command to be executed.
        command = build_command(step)

        while True:
            # Print the step name and the script name to be executed.
            if log_file:
                logger.info(f"Processing Step {i+1}: {step.script}...")
            else:
                click.echo(termcolor.colored(f"Processing Step {i+1}: {step.script}...", "yellow"))

            # Execute the step.
            try:
                # Default the return code to 0.
                return_code = 0

                if log_file:
                    logger.info("-" * 20 + " Output " + "-" * 20)
                else:
                    click.echo("-" * 20 + " Output " + "-" * 20)

                # Execute the step and capture the output.
                if log_file:
                    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    logger.info("\n" + output.decode("utf-8").rstrip())
                else:
                    subprocess.check_call(command, stderr=subprocess.STDOUT, shell=True)

                if log_file:
                    logger.info("-" * 20 + "--------" + "-" * 20)
                else:
                    click.echo("-" * 20 + "--------" + "-" * 20)

            except subprocess.CalledProcessError as e:
                # If the step fails, print the error and set the return code to the error code.
                if log_file:
                    logger.error(e.output.decode("utf-8").rstrip())
                    logger.info("-" * 20 + "--------" + "-" * 20)
                    logger.error(f"Step {i+1} ({step.script}) failed with error: {e}.")
                else:
                    click.echo("-" * 20 + "--------" + "-" * 20)
                    click.echo(termcolor.colored(f"Step {i+1} ({step.script}) failed with error: {e}.", "red"))

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
                response = click.prompt(termcolor.colored("Do you want to rerun this step? (y/n)", "blue"))

                # If the user selects to retry, restart the step.
                if response.lower() == "y":
                    click.echo("Restarting step...")
                else:
                    response = click.prompt(
                        termcolor.colored(
                            "Do you want to rerun the whole pipeline from the beginning? (y/n)",
                            "blue",
                        )
                    )
                    # If the user selects to restart the pipeline, restart the pipeline.
                    if response.lower() == "y":
                        click.echo(termcolor.colored("Restarting pipeline...", "yellow"))
                        linker(cfg, log_file, non_interactive, keep_running, bsched)
                        return 0
                    else:
                        click.echo(termcolor.colored("Exiting...", "red"))
                        return 1

            # If the return code is 0, the step completed successfully.
            else:
                if log_file:
                    logger.info(f"Step {i+1} ({step.script}) completed successfully.")
                else:
                    click.echo(
                        termcolor.colored(
                            f"Step {i+1} ({step.script}) completed successfully.",
                            "green",
                        )
                    )
                break

    return 0


if __name__ == "__main__":
    fire.Fire(scheduler)
