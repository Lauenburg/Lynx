# crude-link
A rudimentary flow logic that links multiple subtasks together and executes them sequentially.

## ML Process Scheduler Tool

This Python tool is designed to automate the execution of an ML process with several steps, including data processing, training, validation, and deployment. The tool is comprised of a Hydra config file and a Python script called `scheduler.py`.

### Hydra Config File

The Hydra config file (`config.yaml`) is used to specify the execution steps of the ML process. The file uses YAML syntax and is structured as follows:

```yaml
defaults:
  - data_processing: &data_processing
  - training: &training
  - validation: &validation
  - deployment: &deployment

steps:
  - <<: *data_processing
  - <<: *training
  - <<: *validation
  - <<: *deployment
```

The `defaults` section defines the script and arguments for each step, which are then referenced in the steps section to execute the `steps` sequentially. Note that the `arguments` section under each step specifies the key-value pairs that will be passed as arguments to the corresponding Python script.

### Scheduler Script

The `scheduler.py` script processes the hydra config file sequentially. For each step in the hydra config, the scheduler calls the referenced script, passing the provided list of key-value pairs as function arguments. If the function returns zero, the scheduler calls the function of the next step, and so on, until no further steps are available. If a step fails, the scheduler prints a warning and starts a dialog asking if the particular step or the whole pipeline should be rerun.

### Requirements
- Python 3.6 or higher
- Hydra

### Usage
1. Install the requirements: `pip install -r requirements.txt`
2. Define the execution steps in the Hydra config file (`config.yaml`)
3. Run the scheduler: `python scheduler.py`