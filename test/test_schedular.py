import os

import omegaconf
import pytest

from schedular import build_command, linker, load_config


# test the dummy config ensuring that it can be passed to a valid omegaconf object
def test_load_config() -> None:
    """Test that the config file can be loaded."""
    config = load_config("conf/config.yaml")
    assert isinstance(config, omegaconf.dictconfig.DictConfig)


# test the dummy config by ensuring that the build_command function processes it correctly
def test_build_command() -> None:
    """Test that the command can be built."""
    config = load_config("conf/config.yaml")
    try:
        command = build_command(config.steps[0])
        assert isinstance(command, str)
    except Exception as e:
        pytest.fail(e)


# test that the schedular runs through with out error, running it in non-interactive mode
def test_linker() -> None:
    """Test that the pipeline runs through without error."""
    config = load_config("conf/config.yaml")
    try:
        linker(config, "lynx.log", True)
    except Exception as e:
        pytest.fail(e)
    finally:
        # delete the log file
        os.remove("lynx.log")
