# crude-link
A rudimentary flow logic that links multiple subtasks together and executes them sequentially.

## ML Process Scheduler Tool

This Python tool is designed to automate the execution of an ML process with several steps, like data processing, training, validation, and deployment. 
The tool is comprised of a Hydra config file and a Python script called `scheduler.py`.

### Hydra Config File

The Hydra config file (`config.yaml`) is used to specify the execution steps of the ML process. The file uses YAML syntax and is structured as follows:

```yaml
default:
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

The user can specify an arbitrary number of steps. Note that the `arguments` section under each step specifies the key-value pairs that will be passed as arguments to the corresponding Python script.
The config's step section references the configs in the default section. The `&` symbol defines an alias for a config, and the `<<` symbol references the config. 
Script and file paths can be absolute or relative to the location of the root folder. The user should obviously make sure that the referenced scripts exist.
It is expected that the referenced scripts return a zero value if the execution was successful and, otherwise, a non-zero value.

### Scheduler Script

The `scheduler.py` script processes the hydra config file sequentially. For each step in the hydra config, the scheduler calls the referenced script, passing the provided list of key-value pairs as function arguments. 
If the function returns zero, the scheduler calls the function of the next step, and so on, until no further steps are available. 
If a step fails, the scheduler prints a warning and starts a dialog asking if the particular step or the whole pipeline should be rerun.

### Requirements
- Python 3.6 or higher
- Hydra
- termcolor

### Usage
1. Install the requirements: `pip install -r requirements.in`
2. Define the execution steps in the Hydra config file (`config.yaml`)
3. Run the scheduler: `python scheduler.py`


### Cronjob
Schedule the execution of the scheduler script with a cronjob. For example, to run the scheduler every Monday at 10am, add the following line to the crontab file:
```bash
0 10 * * 1 python /path/to/scheduler.py
```