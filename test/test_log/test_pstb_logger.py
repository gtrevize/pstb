"""
This module contains unit tests for the `pstb_logger` module.

The `pstb_logger` module provides functions and classes for setting up and configuring logging in the PSTB application.
"""

import logging
import os
import re
import sqlite3
import sys

import pytest

# Add the src directory to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from pstb.log import (  # noqa: E402 - ignore module level import not at top of file due to sys.path.insert
    pstb_logger,
)

pattern_info = re.compile(r"(\bINFO\b)\s+(\S+):(\S+):(\d+)\s+(.+)")
pattern_error = re.compile(r"(\bERROR\b)\s+(\S+):(\S+):(\d+)\s+(.+)")


@pytest.fixture
def logger():
    # Reset the logger
    pstb_logger.logger = None
    pstb_logger.setup_logger()

    return pstb_logger.logger


def test_setup_logger(logger):
    """
    Test case for setup_logger function.

    It verifies that the logger object is an instance of logging.Logger class.
    """
    pstb_logger.setup_logger()
    assert isinstance(logger, logging.Logger)


def test_set_default_handler(logger):
    """
    Test case for set_default_handler function.

    It verifies that the specified handler is added to the logger's handlers list.
    """
    handler = logging.StreamHandler()
    pstb_logger.set_default_handler(handler)
    assert handler in logger.handlers


def test_set_log_level(logger):
    """
    Test case for set_log_level function.

    It verifies that the logger's log level is set to the specified level.
    """
    pstb_logger.set_log_level(logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_set_temporary_level(logger):
    """
    Test case for set_temporary_level function.

    It verifies that the logger's log level is temporarily set to the specified level within the context.
    """

    with pstb_logger.set_temporary_level(logging.DEBUG):
        assert logger.level == logging.DEBUG
    assert logger.level == logging.INFO


def test_get_log_level(logger):
    """
    Test case for get_log_level function.

    It verifies that the returned log level matches the logger's log level.
    """
    assert pstb_logger.get_log_level() == logger.level


def test_set_log_level_debug(logger):
    """
    Test case for set_log_level_debug function.

    It verifies that the logger's log level is set to DEBUG.
    """
    pstb_logger.set_log_level_debug()
    assert logger.level == logging.DEBUG


def test_set_log_level_info(logger):
    """
    Test case for set_log_level_info function.

    It verifies that the logger's log level is set to INFO.
    """
    pstb_logger.set_log_level_info()
    assert logger.level == logging.INFO


def test_set_log_level_warning(logger):
    """
    Test case for set_log_level_warning function.

    It verifies that the logger's log level is set to WARNING.
    """
    pstb_logger.set_log_level_warning()
    assert logger.level == logging.WARNING


def test_set_log_level_error(logger):
    """
    Test case for set_log_level_error function.

    It verifies that the logger's log level is set to ERROR.
    """
    pstb_logger.set_log_level_error()
    assert logger.level == logging.ERROR


def test_set_log_level_critical(logger):
    """
    Test case for set_log_level_critical function.

    It verifies that the logger's log level is set to CRITICAL.
    """
    pstb_logger.set_log_level_critical()
    assert logger.level == logging.CRITICAL


# Resorting to caplog because capsys doesn't capture logging output.
# not
# https://docs.pytest.org/en/latest/logging.html#caplog-basic-usage
def test_set_output_to_console(logger, caplog: pytest.LogCaptureFixture):
    """
    Test case for set_output_to_console function.

    It verifies that a StreamHandler is added to the logger's handlers list and the test message
    set to be displayed on the console. We can't verify that the message is actually displayed on the console,
    because capsys doesn't capture logging output. Not even forcing a flush on the handler works.
    """
    pstb_logger.set_output_to_console()
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    logger.info("Test message")
    logger.handlers[0].flush()
    result = re.search(pattern_info, caplog.text)
    assert result is not None
    assert result.group(5) == "Test message"


def test_set_output_to_file(logger):
    """
    Test case for set_output_to_file function.

    It verifies that a FileHandler is added to the logger's handlers list and the test message is
    written to the logfile.
    """
    file_path = "test.log"
    pstb_logger.set_output_to_file(file_path)
    assert isinstance(logger.handlers[0], logging.FileHandler)

    # Verify that the test message is written to the logfile
    logger.info("Test message")
    logger.handlers[0].flush()
    with open(file_path, "r") as f:
        content = f.read()
    assert "Test message" in content

    os.remove(file_path)


def test_set_output_to_database(logger):
    """
    Test case for set_output_to_database function.

    It verifies that a DatabaseHandler is added to the logger's handlers list and the test message is inserted
    into the database.
    """
    db_filename = "test.db"
    pstb_logger.set_output_to_database(db_filename)
    assert isinstance(logger.handlers[0], pstb_logger.DatabaseHandler)

    # Verify that the test message is inserted into the database
    logger.info("Test message")

    # Use the real database filename; could be different from the one specified
    real_db_filename = logger.handlers[0].db_filename
    conn = sqlite3.connect(real_db_filename)
    cursor = conn.cursor()
    cursor.execute(f"SELECT message FROM {logger.name}")
    result = cursor.fetchall()
    conn.close()
    assert ("Test message",) in result

    os.remove(real_db_filename)


def test_add_output_to_console(logger, caplog: pytest.LogCaptureFixture):
    """
    Test case for add_output_to_console function.

    It verifies that a StreamHandler is added to the logger's handlers list and the test message
    set to be displayed on the console. We can't verify that the message is actually displayed on the console,
    because capsys doesn't capture logging output. Not even forcing a flush on the handler works.
    """
    pstb_logger.add_output_to_console()
    assert isinstance(logger.handlers[-1], logging.StreamHandler)

    # Verify that the test message is displayed on the console
    logger.info("Test message")
    logger.handlers[0].flush()
    result = re.search(pattern_info, caplog.text)
    assert result is not None
    assert result.group(5) == "Test message"


def test_add_output_to_file(logger):
    """
    Test case for add_output_to_file function.

    It verifies that a FileHandler is added to the logger's handlers list and the test message is
    written to the logfile.
    """
    file_path = "test.log"
    pstb_logger.add_output_to_file(file_path)
    assert isinstance(logger.handlers[-1], logging.FileHandler)

    # Verify that the test message is written to the logfile
    logger.info("Test message")
    logger.handlers[0].flush()
    with open(file_path, "r") as f:
        content = f.read()
    assert "Test message" in content

    os.remove(file_path)


def test_add_output_to_database(logger):
    """
    Test case for add_output_to_database function.

    It verifies that a DatabaseHandler is added to the logger's handlers list and the test message is inserted
    into the database.
    """
    db_filename = "test.db"
    pstb_logger.add_output_to_database(db_filename)
    assert isinstance(logger.handlers[-1], pstb_logger.DatabaseHandler)

    # Verify that the test message is inserted into the database
    logger.info("Test message")

    # Use the real database filename; could be different from the one specified
    real_db_filename = logger.handlers[-1].db_filename
    conn = sqlite3.connect(real_db_filename)
    cursor = conn.cursor()
    cursor.execute(f"SELECT message FROM {logger.name}")
    result = cursor.fetchall()
    conn.close()
    assert ("Test message",) in result

    os.remove(real_db_filename)


def test_suppress_repeat_filter():
    """
    Test case for SuppressRepeatFilter class.

    It verifies that the filter filters out repeated log records.
    """
    filter = pstb_logger.SuppressRepeatFilter()
    record = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    # record2 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    assert filter.filter(record)
    assert filter.filter(record)
    assert filter.filter(record)
    assert not filter.filter(record)


def test_suppress_repeat_filter_max_repetitions():
    """
    Test case for SuppressRepeatFilter class with max_repetitions parameter.

    It verifies that the filter filters out repeated log records up to the specified maximum repetitions.
    """
    filter = pstb_logger.SuppressRepeatFilter(max_repetitions=1)
    record1 = logging.LogRecord("test", logging.INFO, "", 0, "Test message 1", None, None)
    assert filter.filter(record1)
    assert not filter.filter(record1)
    assert not filter.filter(record1)
    record2 = logging.LogRecord("test", logging.INFO, "", 0, "Test message 2", None, None)
    assert filter.filter(record2)


def test_set_invalid_log_level(logger):
    """
    Test case for set_invalid_log_level function.

    It verifies that a ValueError is raised when an invalid log level is specified.
    """
    with pytest.raises(ValueError):
        pstb_logger.set_log_level("invalid_level")


def test_set_output_to_nonexistent_database(logger):
    """
    Test case for set_output_to_nonexistent_database function.

    It verifies that a FileNotFoundError is raised when a non-existent database file is specified.
    """
    with pytest.raises(FileNotFoundError):
        pstb_logger.set_output_to_database("nonexistent.db", dont_create=True)


def test_other_error_conditions(logger):
    """
    Test case for other_error_conditions function.

    It verifies the error conditions and raised exceptions for various scenarios.
    """

    # Test SuppressRepeatFilter with invalid max repetitions
    with pytest.raises(ValueError):
        _ = pstb_logger.SuppressRepeatFilter(max_repetitions=-1)

    # Test set_output_to_file with invalid file path
    with pytest.raises(FileNotFoundError):
        pstb_logger.set_output_to_file("/dev/null/nonexistent.db", dont_create=True)

    # Test add_output_to_file with invalid file path
    with pytest.raises(FileNotFoundError):
        pstb_logger.add_output_to_file("/dev/null/nonexistent.db", dont_create=True)
