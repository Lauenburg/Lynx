import logging
import os

import omegaconf
import pytest

from scheduler import build_command, linker, load_config, setup_logger


def test_load_config() -> None:
    """Test that the config file can be passed to a valid omegaconf object."""
    config = load_config("conf/config.yaml")
    assert isinstance(config, omegaconf.dictconfig.DictConfig)


def test_build_command() -> None:
    """Test that the command can be built."""
    config = load_config("conf/config.yaml")
    try:
        command = build_command(config.steps[0])
        assert isinstance(command, str)
    except Exception as e:
        pytest.fail(e)


def test_setup_logger() -> None:
    """Test that the logger can be set up."""
    try:
        logger = setup_logger("lynx.log")
        assert isinstance(logger, logging.Logger)
    except Exception as e:
        pytest.fail(e)


def test_linker() -> None:
    """Test that the pipeline runs through without error."""
    config = load_config("conf/config.yaml")
    logger = setup_logger("lynx.log")

    try:
        linker(config, logger, True)
    except Exception as e:
        pytest.fail(e)
    finally:
        # delete the log file
        os.remove("lynx.log")
