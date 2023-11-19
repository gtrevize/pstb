"""
This module contains unit tests for the `pstb_logger` module.

The `pstb_logger` module provides functions and classes for setting up and configuring logging in the PSTB application.
"""

import logging
import os
import sqlite3

import pytest

from src.pstb.log import pstb_logger

# sys.path.append("../../../")
# import pstb_logger


@pytest.fixture
def logger():
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
    with pstb_logger.set_temporary_level(logging.INFO):
        assert logger.level == logging.INFO
    assert logger.level == logging.DEBUG


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


def test_set_output_to_console(logger, capsys):
    """
    Test case for set_output_to_console function.

    It verifies that a StreamHandler is added to the logger's handlers list and the test message is displayed on the console.
    """
    pstb_logger.set_output_to_console()
    assert isinstance(logger.handlers[0], logging.StreamHandler)

    # Verify that the test message is displayed on the console
    logger.info("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_set_output_to_file(logger):
    """
    Test case for set_output_to_file function.

    It verifies that a FileHandler is added to the logger's handlers list and the test message is written to the logfile.
    """
    file_path = "test.log"
    pstb_logger.set_output_to_file(file_path)
    assert isinstance(logger.handlers[0], logging.FileHandler)

    # Verify that the test message is written to the logfile
    logger.info("Test message")
    with open(file_path, "r") as f:
        content = f.read()
    assert "Test message" in content

    os.remove(file_path)


def test_set_output_to_database(logger):
    """
    Test case for set_output_to_database function.

    It verifies that a DatabaseHandler is added to the logger's handlers list and the test message is inserted into the database.
    """
    db_filename = "test.db"
    pstb_logger.set_output_to_database(db_filename)
    assert isinstance(logger.handlers[0], pstb_logger.DatabaseHandler)

    # Verify that the test message is inserted into the database
    logger.info("Test message")
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM log")
    result = cursor.fetchall()
    conn.close()
    assert ("Test message",) in result

    os.remove(db_filename)


def test_add_output_to_console(logger, capsys):
    """
    Test case for add_output_to_console function.

    It verifies that a StreamHandler is added to the logger's handlers list and the test message is displayed on the console.
    """
    pstb_logger.add_output_to_console()
    assert isinstance(logger.handlers[-1], logging.StreamHandler)

    # Verify that the test message is displayed on the console
    logger.info("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_add_output_to_file(logger):
    """
    Test case for add_output_to_file function.

    It verifies that a FileHandler is added to the logger's handlers list and the test message is written to the logfile.
    """
    file_path = "test.log"
    pstb_logger.add_output_to_file(file_path)
    assert isinstance(logger.handlers[-1], logging.FileHandler)

    # Verify that the test message is written to the logfile
    logger.info("Test message")
    with open(file_path, "r") as f:
        content = f.read()
    assert "Test message" in content

    os.remove(file_path)


def test_add_output_to_database(logger):
    """
    Test case for add_output_to_database function.

    It verifies that a DatabaseHandler is added to the logger's handlers list and the test message is inserted into the database.
    """
    db_filename = "test.db"
    pstb_logger.add_output_to_database(db_filename)
    assert isinstance(logger.handlers[-1], pstb_logger.DatabaseHandler)

    # Verify that the test message is inserted into the database
    logger.info("Test message")
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM log")
    result = cursor.fetchall()
    conn.close()
    assert ("Test message",) in result

    os.remove(db_filename)


def test_database_handler_emit():
    """
    Test case for DatabaseHandler emit method.

    It verifies that the test message is inserted into the database.
    """
    handler = pstb_logger.DatabaseHandler()
    handler.connect_to_database()
    record = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    handler.emit(record)
    handler.close()

    # Verify that the test message is inserted into the database
    conn = sqlite3.connect(handler.db_filename)
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM log")
    result = cursor.fetchall()
    conn.close()
    assert ("Test message",) in result


def test_database_handler_close():
    """
    Test case for DatabaseHandler close method.

    It verifies that the database connection is closed.
    """
    handler = pstb_logger.DatabaseHandler()
    handler.connect_to_database()
    handler.close()
    assert handler.conn is None


def test_suppress_repeat_filter():
    """
    Test case for SuppressRepeatFilter class.

    It verifies that the filter filters out repeated log records.
    """
    filter = pstb_logger.SuppressRepeatFilter()
    record1 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    record2 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    assert filter.filter(record1)
    assert not filter.filter(record2)


def test_suppress_repeat_filter_max_repetitions():
    """
    Test case for SuppressRepeatFilter class with max_repetitions parameter.

    It verifies that the filter filters out repeated log records up to the specified maximum repetitions.
    """
    filter = pstb_logger.SuppressRepeatFilter(max_repetitions=2)
    record1 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    record2 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    record3 = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
    assert filter.filter(record1)
    assert not filter.filter(record2)
    assert not filter.filter(record3)


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
        pstb_logger.set_output_to_database("nonexistent.db")


def test_other_error_conditions(logger):
    """
    Test case for other_error_conditions function.

    It verifies the error conditions and raised exceptions for various scenarios.
    """
    # Test DatabaseHandler with invalid log name
    with pytest.raises(ValueError):
        handler = pstb_logger.DatabaseHandler(log_name="invalid_log_name")

    # Test DatabaseHandler with non-existent database file
    with pytest.raises(FileNotFoundError):
        handler = pstb_logger.DatabaseHandler(db_filename="nonexistent.db")

    # Test DatabaseHandler emit method with closed database connection
    handler = pstb_logger.DatabaseHandler()
    with pytest.raises(sqlite3.ProgrammingError):
        record = logging.LogRecord("test", logging.INFO, "", 0, "Test message", None, None)
        handler.emit(record)

    # Test SuppressRepeatFilter with invalid max repetitions
    with pytest.raises(ValueError):
        _ = pstb_logger.SuppressRepeatFilter(max_repetitions=-1)

    # Test set_output_to_file with invalid file path
    with pytest.raises(ValueError):
        pstb_logger.set_output_to_file("invalid_file_path")

    # Test add_output_to_file with invalid file path
    with pytest.raises(ValueError):
        pstb_logger.add_output_to_file("invalid_file_path")

    # Test add_output_to_database with non-existent database file
    with pytest.raises(FileNotFoundError):
        pstb_logger.add_output_to_database("nonexistent.db")

    # Test add_output_to_database with invalid log name
    with pytest.raises(ValueError):
        pstb_logger.add_output_to_database("valid.db", log_name="invalid_log_name")

    # Test add_output_to_database with invalid formatter
    with pytest.raises(ValueError):
        pstb_logger.add_output_to_database("valid.db", formatter="invalid_formatter")
