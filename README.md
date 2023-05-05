# Lynx
Lynx (pronounced "Links") is a simple flow logic tool that links multiple subtasks together and executes them sequentially. The tool is designed to automate the execution of an ML process with several steps, such as data processing, training, validation, and deployment. Lynx relies on a simple YAML configuration file to specify the flow. The tool processes the steps sequentially and can be run interactively or non-interactively. The results can either be logged or printed to standard output. Further, the user can run the pipeline once or specify a cronjob-like schedule to run the pipeline regularly. Finally, Lynx can run your pipeline in the foreground or the background as a subprocess.

We designed Lynx to be as intuitive and lightweight as possible while providing maximum flexibility through simplicity. Lynx serves the simple single purpose of scheduling and sequentially executing tasks. It neither tries to be a swiss army knife nor is it intended for production. At the current stage, the tool is rather intended for research pipelines, testing, and debugging. Lynx is written in Python and uses the [APScheduler](https://apscheduler.readthedocs.io/en/stable/) package to schedule the pipeline.

## Requirements
- Python 3.6 or higher
- Pip packages as listed in `setup.py`

## Preparation
All scripts that the Lynx should execute must be callable and pass the provided arguments to the relevant function.
To make your scripts callable, add the `if __name__ == '__main__':` statement to the end of each script and call the script's main function.
To pass the arguments to the main function of a script, you can use the `fire` pip package that is part of the `Lynx` requirements.

Example for a function called `main` that takes two arguments:
```python
import fire

def main(args1: str, args2: int):
  pass

if __main__ == '__main__':
    fire.Fire(main)
```

## Quick start:
You can use the tool as a script or a command line tool.
In both cases, you should first activate a virtual environment.

### Script
```bash
python setup.py install # install the requirements
python lynx.py start --config-file conf/config.yaml # run the pipeline
```

### Command Line Tool
```bash
python install -e .
lynx start --config-file conf/config.yaml --background --log-file lynx.log # run the pipeline in the background and log the output to lynx.log
lynx stop # stop the pipeline, only works if the pipeline is executed in the background, otherwise use Ctrl + C or Ctrl + D
```

#### Arguments

- `--config-file` (`-cf`): Path to the yaml config file. Default: `conf/config.yaml`
- `--log-file` (`-lf`): If provided, stdout will be written to a log file. However, the logs will also show on the screen - use `--background` for silent mode. Default: `None`
- `--log-level` (`-ll`): Set the log level for the logs streamed to the screen when running in the forground. Default: `INFO`
- `--log-size` (`-ls`): Set the log file size in bytes. Default: `2097152` (2*1024*1204 = ~2MB)
- `--log-backup-count` (`-lbc`): Set the number of log files to keep. Default: `3`
- `--non-interactive` (`-ni`): Run Lynx in non-interactive mode, i.e., toggle the error recovery dialog. Default: `False`
- `--keep-running` (`-kr`): Keep the cronjob schedule running even if a step fails. Default: `False`
- `--background` (`-bg`): Run Lynx in the background as a subprocess.  The user is prompted to provide a log file if not done so. If none is provided, stdout is discarded. If a log file is provided, stdout will be written to a log file. Default: `False`

## Scheduler

Lynx processes the `step` section of the yaml config file sequentially. For each step in the config, Lynx calls the referenced script, passing the provided list of function arguments. Suppose the main function of the called script returns a zero return value. In that case, Lynx executes the script of the next step, and so on, until no further steps are available.

### Interactive Mode
If the function returns a non-zero return value, Lynx prints a warning and starts a dialog asking if the particular step or the whole pipeline should be rerun. If the user chooses to rerun the step, Lynx calls the function of the step again. If the user chooses to rerun the whole pipeline, Lynx starts from the beginning.

*Starting Lynx in interactive and *
```bash
lynx start --config-file config.yaml # run the pipeline
```

### Non-Interactive Mode
When setting the `--non-interactive` (`-ni`) flag, Lynx will stop asking for user-input in case it encounters an error, but it will keep printing the output to the screen. If the user provides a log file the screen output will additionaly be logged to the provided file. The user can specify the name and path for the log file using the `--log-file` (`lf`) argument. If the log file already exists, Lynx will append the log to the existing file. If the log file does not exist, Lynx creates a new one. The size of the log file can be set using the `--log-size` (`-ls`) flag. The backup count can be set using the `--log-backup-count` (`-lbc`) flag. This means Lynx will keep the last 3 log files.
If Lynx is run in non-interactive mode, the `cron` section of the yaml config file is used to schedule the execution of the pipeline. If the `cron` section is omitted, Lynx will run the pipeline only once. If a job fails, Lynx will stop the execution of the pipeline and the cronjob schedule. The user can set the `--keep-running` flag to keep the cronjob schedule running even if a step fails. This means Lynx will try to rerun the pipeline at the next scheduled time.
To run Lynx silently in the background, the user can set the `--background` flag. The user is prompted to provide a log file if not done so. If none is provided, stdout is discarded. If a log file is provided, stdout will be written to a log file.
Providing the `--background` flag automatically also sets the `--non-interactive` flag.

```bash
lynx start --config-file conf/config.yaml --non-interactive # run the pipline in non-interactive mode
```

### Stop Lynx
Lynx can be stopped by pressing `Ctrl + C` or `Ctrl + D` when running in the foreground.
If the user starts Lynx in the background, Lynx can be stopped using the stop command.
```bash
lynx start --config-file conf/config.yaml --background # run the pipeline in the background
lynx stop # stop the pipeline
```

The `stop` comment will stop the pipeline and the cronjob schedule. We can kill the orphaned subprocess (the main script already terminated) as we log the process information to `.lynx_pid.json` in the current directory. The stop function will read the pid from the `.lynx_pid.json` file, retrieve the current corresponding process information using `psutil` and ask for confirmation for the kill the process. The `.lynx_pid.json` file will always only contain a single reference to the latest scheduler that was executed in the background. Thus the user should only run a single scheduler in the background at a time or handle the process termination manually (`ps -ax | grep lynx` and `kill -9 <pid>`). Should you regularly run multiple schedulers in the background, feel free to open a pull request to improve the process management.

### Arguments

Lynx can be run with the following arguments:
- `--config-file` (`-cf`): Path to the yaml config file. Default: `conf/config.yaml`
- `--log-file` (`-lf`): If provided, stdout will be written to a log file. However, the logs will also show on the screen - use `--background` for silent mode. Default: `None`
- `--log-level` (`-ll`): Set the log level for the logs streamed to the screen when running in the forground. Default: `INFO`
- `--log-size` (`-ls`): Set the log file size in bytes. Default: `2097152` (2*1024*1204 = ~2MB)
- `--log-backup-count` (`-lbc`): Set the number of log files to keep. Default: `3`
- `--non-interactive` (`-ni`): Run Lynx in non-interactive mode, i.e., toggle the error recovery dialog. Default: `False`
- `--keep-running` (`-kr`): Keep the cronjob schedule running even if a step fails. Default: `False`
- `--background` (`-bg`): Run Lynx in the background as a subprocess.  The user is prompted to provide a log file if not done so. If none is provided, stdout is discarded. If a log file is provided, stdout will be written to a log file. Default: `False`

**Sample Uses**
- If you provide the `--non-interactive` (`-ni`) flag the feedback is printed to the terminal, the pipeline terminates in case an error is encountered.
- If you provide the `--non-interactive` (`-ni`) flag and the `--log-file` (`-lg`) flag the feedback will be written to the log file and the screen, the pipeline terminates in case an error is encountered.
- If you provide the `--non-interactive` (`-ni`) flag, a crone job schedule in the config file and the `--keep-running` (`-kp`) flag the feedback is printed to the terminal, the pipeline terminates in case an error is encountered, but Lynx will keep scheduling new runs.
- If you provide the `--background` (`-bg`), `--non-interactive` (`-ni`) is automatically set to true, and you will be prompted to provide  a log-file name. If you simply press enter on the prompt the pipeline will run in the background and the print and log output will be discarded. If you provide a log file name the output will be written to the file.
You can obviously also provide the `--log-file` (`-lg`) flag to circumvent the prompt.

## YAML Config File

The yaml config file is used to specify the execution steps of the ML process as well as the scheduling of the process.
The yaml comprises the following three sections:

- step [required]: The list of steps that should be executed.
- configs [required]: The step-specific scripts and arguments
- cron [optional]: Time specifications for the scheduler

The `steps` section of the yaml config file lists the steps that should be executed. The steps are executed sequentially, thus, the order matters. Each step references a config that is defined in the `configs` section.

The `configs` section specifies the scripts and the corresponding function arguments. The `script` section of each step specifies the path to the Python script that should be executed. The `arguments` section lists all arguments, options, flags, parameters or similar that should be passed to the corresponding Python script. You can either specify all parameters in one list element or split them into separate ones, like:
```yaml
arguments:
  - "--input_file data/dummy.data"
  - "nr_images=500"
  - "filter=true"
```
or
```yaml
arguments:
  - "--input_file data/dummy.data nr_images=500 filter=true"
```
We chose this format for maximum flexibility, allowing the passing of unusual argument structures while providing a semi-structured layout that facilitates readability when there are multiple configs with different experiment settings.
If Lynx is run from the same directory as the config file, the paths can be relative to the config file. If Lynx is run from a different directory, the paths must be absolute.

The `cron` section specifies the cronjob schedule that can be used for running the pipeline regularly. However, the cronjob schedule is only used if the `--non-interactive` (`-ni`) or the `--background` (`-bg`) flag is set. If you provide neither of those two flags, the cronjob schedule is ignored and can be omitted from the yaml config file. If you do not add the `cron` section to the yaml config file, the pipeline will run once and terminate, even when setting `--non-interactive` (`-ni`) or `--background` (`-bg`).
See the [Cron Scheduling Examples](#cron-scheduling-examples) section for more examples.
How to configure the schedule is specified on the [apscheduler.triggers.cron](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html#module-apscheduler.triggers.cron) homepage. 

The following example shows a yaml config file with all available options. The file defines the four steps `preprocess`, `training`, `validation`, and `deployment`. The `preprocess` step calls the `preprocess.py` script with the arguments `input_file`, `nr_images`, and `filters`. All the arguments are listed as separate list entries. The `training` step calls the `train.py` script without any arguments. The `validation` step calls the `validate.py` script with the argument `input_file` and `42`. Both arguments are passed using a single list entry. The `deployment` step calls the `deploy.py` script without any arguments. The scheduler will run the pipeline every 10 seconds on Thursdays if executed with the `--non-interactive` flag.

```yaml
cron:
  day_of_week: thu
  hour: '*'
  minute: '*'
  second: '*/10'

configs:
  - preprocess: &preprocess
        - script: tasks/preprocess.py
          arguments:
            - "--input_file data/dummy.data"
            - "nr_images=500"
            - "filter=true"
  - training: &training
      - script: tasks/train.py
  - validation: &validation
      - script: tasks/validate.py
        arguments:
          - "--input_file data/dummy.data --forty_two 42"
  - deployment: &deployment
      - script: tasks/deploy.py

steps:
  - <<: *preprocess
  - <<: *training
  - <<: *validation
  - <<: *deployment
```


### Cron Scheduling Examples

Example cron settings for the scheduler:

- Run the scheduler every day at 10 am:
  ```yaml
  cron:
    hour: 10
    minute: 0
    second: 0
  ```
- Run the scheduler every first Friday of the month at 2 pm:
  ```yaml
  cron:
    day: 1
    day_of_week: 'fri'
    hour: 14
    minute: 0
    second: 0
  ```
- Run the scheduler every 10 minutes:
  ```yaml
  cron:
    minute: '*/10'
  ```

## Tests

Run the tests with:
```bash
python -m pytest test
```
