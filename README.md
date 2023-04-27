# crude-link
A rudimentary flow logic that links multiple subtasks together and executes them sequentially. Crude-link is designed to automate the execution of an ML process with several steps, like data processing, training, validation, and deployment. Crude-link relies on a simple YAML config file to specify the flow.

## Requirements
- Python 3.6 or higher
- `termcolor`
- `omegaconf`
- `apscheduler`
- `click`

## Preparation
All scripts the scheduler should execute must be callable and pass the provided arguments to the relevant function.
To make the script callable, add the `if __name__ == '__main__':` statement to the end of the script and call your main function.
To pass the arguments to the main function, you can use the `fire` pip package that is part of the `crude-link` requirements.

Example for a function called `main` that takes two arguments:
```python
def main(args1: str, args2: int):
  pass

if __main__ == '__main__':
    fire.Fire(main)
```

## Usage
You can use the tool as a script or a command line tool.
In both cases, you should first activate a virtual environment.

### Script
```bash
python crude_link/scheduler.py --config-file config.yaml
```

### Command Line Tool
```bash
python install -e .
crude-link --config-file config.yaml
```

## Scheduler

Crude-Link processes the `step` section of the yaml config file sequentially. For each step in the config, the scheduler calls the referenced script, passing the provided list of key-value pairs as function arguments. Suppose the process returns a zero return value. In that case, the scheduler calls the function of the next step, and so on, until no further steps are available.

### Interactive Mode
If the function returns a non-zero return value, the scheduler prints a warning and starts a dialog asking if the particular step or the whole pipeline should be rerun. If the user chooses to rerun the step, the scheduler calls the function of the step again. If the user chooses to rerun the whole pipeline, the scheduler starts from the beginning.

### Non-Interactive Mode
When setting the `--non-interactive` flag, the scheduler will not ask for user input. Instead, the scheduler will log everything. The user can specify the name and path for the log file using the `--log-file` argument. If the log file already exists, the scheduler will append the log to the existing file. If the log file does not exist, the scheduler creates a new one. The size of the log file is limited to 2MB, the backup count is set to 3. This means the scheduler will keep the last 3 log files.
If the scheduler is run in non-interactive mode, the `cron` section of the yaml config file is used to schedule the execution of the pipeline. If the `cron` section is omitted, the scheduler will run the pipeline only once. If a stab failes, the scheduler will stop the execution of the pipeline and the cronjob schedule. The user can set the `--keep-running` flag to keep the cronjob schedule running even if a step fails. This means the scheduler will try to rerun the pipeline at the next scheduled time.

### Arguments

The scheduler can be run with the following arguments:
- `--config-file`: Path to the yaml config file. Default: `config.yaml`
- `--non-interactive`: Run the scheduler in non-interactive mode. Default: `False`
- `--log-file`: Path to the log file. Default: `crude-link.log`
- `--keep-running`: Keep the cronjob schedule running even if a step fails. Default: `False`


## YAML Config File

The yaml config file is used to specify the execution steps of the ML process as well as the scheduling of the process.
The yaml comprises the following three sections:

- step [required]: The list of steps that should be executed.
- configs [required]: The step specific scripts and arguments
- scheduler [optional]: Time constraints for the scheduler

The `steps` section of the yaml config file lists the steps that should be executed. The steps are executed sequentially, thus, the order matters. Each step references a config that is defined in the `configs` section.

The `configs` section specifies the scripts and the corresponding function arguments for each step. The `arguments` section of each step specifies key-value pairs that will be passed as arguments to the corresponding Python script that gets specified using the `script` keyword. Script and file paths can be absolute or relative depending on where the scheduler is executed.

The `cron` section specifies the cronjob schedule that can be used for running the pipeline regularly. However, the cronjob schedule is only used if the `non_interactive` flag is set to `True`. How to configure the schedule is specified on the [apscheduler.triggers.cron](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html#module-apscheduler.triggers.cron) homepage. If you do not run the scheduler in non-interactive mode, the cronjob schedule is ignored and can be omitted from the yaml config file. See the [Cron Scheduling Examples](#cron-scheduling-examples) section for more examples.

The following example shows a yaml config file with all available options. The file defines the four steps `preproccess`, `training`, `validation`, and `deployment`. The `preproccess` step calls the `preproccess.py` script with the arguments `input_file`, `nr_images`, and `filters`. The `training` step calls the `train.py` script without any arguments. The `validation` step calls the `validate.py` script with the argument `input_file`. The `deployment` step calls the `deploy.py` script without any arguments. The scheduler will run the pipeline every 10 seconds on Thursdays if executed with the `--non-interactive` flag.

```yaml
cron:
  day_of_week: 'thu'
  hour: '*'
  minute: '*'
  second: '*/10'

configs:
  - preproccess: &preproccess
      script: tasks/preproccess.py
      arguments:
        input_file: data/dummy.data
        nr_images: 500
        filters: True
  - training: &training
      script: tasks/train.py
  - validation: &validation
      script: tasks/validate.py
      arguments:
        input_file: data/dummy.data
  - deployment: &deployment
      script: tasks/deploy.py

steps:
  - <<: *preproccess
  - <<: *training
  - <<: *validation
  - <<: *deployment
```


### Cron Scheduling Examples

Example cron settings for the scheduler:

- Run the scheduler every day at 10am:
  ```yaml
  cron:
    hour: 10
    minute: 0
    second: 0
  ```
- Run the scheduler every first Friday of the month at 2pm:
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
