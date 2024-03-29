import json
import os
import signal
import subprocess
import sys

import click
import psutil

from scheduler import scheduler


@click.group("lynx")
def cli() -> None:
    """The main function that runs the pipeline."""
    pass


@cli.command("start")
@click.option(
    "--config-file",
    "-cf",
    type=str,
    default="conf/config.yaml",
    help="The path to the configuration file.",
)
@click.option("--log-file", "-lf", type=str, default=None, help="The path to the log file.")
@click.option(
    "-ll",
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Set the logging level",
)
@click.option("--log_size", "-ls", default=2 * 1024 * 1024, type=int, help="Set the maximum size of the log file.")
@click.option("--log_backup_count", "-lbc", default=3, type=int, help="Set the number of log files to keep.")
@click.option(
    "--non-interactive",
    "-ni",
    is_flag=True,
    default=False,
    help="Run the pipeline in non-interactive mode.",
)
@click.option(
    "--keep-running",
    "-kr",
    is_flag=True,
    default=False,
    help="Stop the current run but keep scheduling new runs in accordance with the cron settings.",
)
@click.option("--background", "-bg", is_flag=True, default=False, help="Run the pipeline in the background.")
def start(
    config_file: str = "conf/config.yaml",
    log_file: str = None,
    log_level: str = "INFO",
    log_size: int = 2 * 1024 * 1024,
    log_backup_count: int = 3,
    non_interactive: bool = False,
    keep_running: bool = False,
    background: bool = False,
) -> None:
    """The main function that starts the scheduler. The scheduler can be run in the foreground or background.

    Args:
        config_file (str): The path to the configuration file.
        log_file (str): The path to the log file.
        log_level (str): The log level.
        log_size (int): The maximum size of the log file.
        log_backup_count (int): The number of log files to keep.
        non_interactive (bool): Run the pipeline in non-interactive mode.
        keep_running (bool): Stop the current run but keep scheduling new runs in accordance with the cron settings.
        background (bool): Run the pipeline in the background.
    """

    # Set non-interactive to true in case that background is True
    if background:
        non_interactive = True

    # check if the config file exists and if not, start a dialog asking for the path to the config file
    if os.path.isfile(config_file) is False:
        config_file = click.prompt(
            "The configuration file does not exist. Please enter the path to the configuration file.",
            type=str,
        )

    # If background is set to True, run the scheduler in the background using subprocess.popen().
    if background and non_interactive:
        # prompt the user to provide a log file if none is provided
        if log_file is None:
            log_file = click.prompt(
                "Please enter the name for the log file, elser the log information will be discarded",
                type=str,
                default="",
            )

        arg = [
            "python",
            "scheduler.py",
            "--config-file",
            config_file,
        ]

        # add the log file flag if a log file is provided
        if log_file:
            arg.extend(["--log-file", log_file])
            arg.extend(["--log-level", log_level])
            arg.extend(["--log-size", str(log_size)])
            arg.extend(["--log-backup-count", str(log_backup_count)])

        # add the non-interactive flag if non-interactive is set to True
        if non_interactive:
            arg.append("--non-interactive")

        # add the keep-running flag if keep-running is set to True
        if keep_running:
            arg.append("--keep-running")

        proc = subprocess.Popen(
            arg,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Write the dict containing the process information of the subprocess to .lynx_pid.log using json.dump().
        with open(".lynx_pid.json", "w") as f:
            json.dump(get_process_info(proc.pid), f)

    else:
        # Run the scheduler in the foreground.
        scheduler(config_file, log_file, log_level, log_size, log_backup_count, non_interactive, keep_running)


# recover the process object from the pickle file and terminate it
@cli.command("stop")
def stop() -> None:
    """Stop the scheduler if it is running in the background."""

    proc = None

    # read the process information from the file as dictionary using json.load()
    with open(".lynx_pid.json") as f:
        proc_info = json.load(f)
        # create a proccess object from the process information
        proc = psutil.Process(proc_info["pid"])

    if proc:
        # Ask the user if they want to terminate the process, providing the process information using the process object
        terminate = click.confirm(f"Are you sure you want to terminate the process: {str(get_process_info(proc.pid))}?")
        if terminate:
            click.echo("Terminating process ... ")
            os.kill(proc.pid, signal.SIGTERM)

            # delete pid log file
            os.remove(".lynx_pid.json")
            exit(0)
    else:
        # If the process is not running, inform the user and exit.
        click.echo("The process is with PID-{proc.pid} allready terminated.")
        exit(0)


def get_process_info(pid: int) -> dict:
    """Get the process information from the process id.

    Args:
        pid (int): The process id.
    """
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return None

    return {
        "pid": process.pid,
        "name": process.name(),
        "exe": process.exe(),
        "cmdline": process.cmdline(),
        "status": process.status(),
        "username": process.username(),
    }


if __name__ == "__main__":
    cli()
