""" 
This module provides a global logger instance that can be used by all modules in the project. 
Functions are provided to set the log level and output to console or file.

Classes:
    DatabaseHandler: A handler that writes log records to a SQLite database.
    SuppressRepeatFilter: A filter that suppresses repeated log messages.

Functions:
    setup_logger: Sets up the global logger instance.
    set_default_handler: Sets the default handler for the global logger instance.
    set_log_level: Sets the log level of the global logger instance.
    set_temporary_level: Sets a temporary log level for the global logger instance.
    get_log_level: Returns the current log level of the global logger instance.
    set_log_level_debug: Sets the log level to DEBUG.
    set_log_level_info: Sets the log level to INFO.
    set_log_level_warning: Sets the log level to WARNING.
    set_log_level_error: Sets the log level to ERROR.
    set_log_level_critical: Sets the log level to CRITICAL.
    set_output_to_console: Sets the output of the global logger instance to console.
    set_output_to_file: Sets the output of the global logger instance to a file.
"""

import atexit
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import colorlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global variable to hold the logger instance
logger = None


#####################
# Classes definitions
#####################


class DatabaseHandler(logging.Handler):
    """
    Creates a handler that writes log records to a SQLite database.
    The database filename can be specified as an argument or read from the PYTHON_LOG_DATABASE environment variable.
    The default filename is the name of the current file with a .db extension.
    Registers a function to close the database when the program exits.

    Args:
        db_filename: The filename of the SQLite database.
        log_name: The name of the log table in the database. Defaults to the name of the current file.
        formatter: The formatter to use for the log records. Defaults to a simple formatter.

    Attributes:
        db_filename: The filename of the SQLite database.
        log_name: The name of the log table in the database.
        conn: The connection to the SQLite database.
        cursor: The cursor for the SQLite database.

    Methods:
        connect_to_database: Connects to the SQLite database.
        emit: Inserts a log record into the database.
        close: Closes the connection to the SQLite database.

    Raises:
        FileNotFoundError: If the database file does not exist.
    """

    def __init__(self, db_filename=None, log_name=None, formatter=None):
        super().__init__()
        if db_filename is None:
            db_filename = os.getenv("PYTHON_LOG_DATABASE", f"{Path(__file__).resolve().with_suffix('')}.db")
        self._db_filename = db_filename
        self.connect_to_database()

        # Set the log name if not specified default to the name of the current file
        if log_name is not None:
            self._log_name = log_name
        else:
            self._log_name = Path(__file__).resolve().stem

        # Set the formatter if specified otherwise use the default formatter
        if formatter is not None:
            self.setFormatter(formatter)
        else:
            # Default formatter
            self.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

        # Register a function to close the database when the program exits
        atexit.register(self.close)

    def connect_to_database(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        # Create a table for logging if it does not exist
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.log_name} (
                timestamp TEXT,
                module TEXT,
                funcName TEXT,
                lineno INTEGER,
                level TEXT,
                message TEXT,
                exception TEXT,
                formatted_message TEXT
            )
        """
        )
        self.conn.commit()

    def emit(self, record):
        # Format the record
        record.message = record.getMessage()
        if self.formatter:
            formatted_message = self.formatter.format(record)
        else:
            formatted_message = record.getMessage()

        # Extract information from the record
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        module = record.module
        funcName = record.funcName
        lineno = record.lineno
        level = record.levelname
        message = record.message
        exception = record.exc_text if record.exc_text else ""

        # Insert log record into the database
        self.cursor.execute(
            """
            INSERT INTO logs (timestamp, module, funcName, lineno, level, message, exception, formatted_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (timestamp, module, funcName, lineno, level, message, exception, formatted_message),
        )
        self.conn.commit()

    def close(self):
        """Closes the connection to the SQLite database."""
        self.conn.close()
        super().close()

    @property
    def log_name(self):
        return self._log_name

    @log_name.setter
    def log_name(self, name):
        self._log_name = name

    @property
    def db_filename(self):
        return self._db_filename

    @db_filename.setter
    def db_filename(self, filename):
        """
        Sets the database filename and connects to the database.

        Args:
            filename: The filename of the SQLite database.

        Raises:
            FileNotFoundError: If the database file does not exist.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Database file '{filename}' does not exist")

        self._db_filename = filename
        self.connect_to_database()


class SuppressRepeatFilter(logging.Filter):
    """
    Suppresses repeated log messages.
    If a log message is repeated more than the maximum number of repetitions, the message is suppressed.
    Reads the maximum number of repetitions from the PYTHON_LOG_MAX_REPETITIONS environment variable or uses the default value of 3.

    Args:
        max_repetitions: The maximum number of repetitions to allow before suppressing the message.

    Attributes:
        max_repetitions: The maximum number of repetitions to allow before suppressing the message.

    Methods:
        filter: Filters log records based on the number of repetitions.
    """

    def __init__(self, max_repetitions=None):
        super().__init__()
        self._last_log = None
        self._repeat_count = 0
        if max_repetitions is None:
            max_repetitions = int(os.getenv("PYTHON_LOG_MAX_REPETITIONS", 3))
        self._max_repetitions = max_repetitions

    def filter(self, record):
        current_log = record.msg
        if current_log == self._last_log:
            self._repeat_count += 1
            # Start suppressing after exceeding maximum repetitions
            return self._repeat_count <= self._max_repetitions
        else:
            if self._repeat_count > self._max_repetitions:
                record.msg += f" [Previous message repeated {self._repeat_count} times]"
            self._last_log = current_log
            self._repeat_count = 0
            return True

    @property
    def max_repetitions(self):
        return self._max_repetitions

    @max_repetitions.setter
    def max_repetitions(self, repetitions):
        self._max_repetitions = repetitions


######################
# Function definitions
######################


def setup_logger():
    """
    Sets up the global logger instance.
    Sets the log level and output based on environment variables.
    Default log level is INFO.
    Default log output is console.
    Default log file is the name of the current file with a .log extension.

    Returns:
        The global logger instance.
    """

    global logger

    # Check if logger is already configured
    if logger is not None:
        return logger

    # Create a logger
    logger = logging.getLogger("my_global_logger")

    # Read log level from environment variable or use default
    log_level = os.getenv("PYTHON_LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Read log output from environment variable
    log_output = os.getenv("PYTHON_LOG_OUTPUT", "console").lower()

    # Set default handler based on the environment variable
    if log_output == "file":
        log_file = os.getenv("PYTHON_LOG_FILE", f"{Path(__file__).resolve().with_suffix('')}.log")
        set_default_handler(logging.FileHandler(log_file))
    elif log_output == "database":
        db_filename = os.getenv("PYTHON_LOG_DATABASE", f"{Path(__file__).resolve().with_suffix('')}.db")
        set_default_handler(DatabaseHandler(db_filename=db_filename))
    else:
        set_default_handler(logging.StreamHandler())

    return logger


def set_default_handler(handler):
    """
    Sets the default handler for the global logger instance.
    Uses a color formatter for console output.
    """

    global logger
    if logger:
        # Remove all existing handlers
        logger.handlers.clear()

        # Create a formatter with color support
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s"
        )

        # Set the formatter for the handler
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)


def set_log_level(level):
    """
    Sets the log level of the global logger.
    Valid levels are DEBUG, INFO, WARNING, ERROR, and CRITICAL.

    Args:
        level: The log level to set.

    Raises:
        ValueError: If the level is not a valid logging level.
    """

    global logger
    if logger:
        if not hasattr(logging, level):
            raise ValueError(
                "'{}' is not a valid logging level. Valid logging levels are {}".format(
                    level, [level for level in dir(logging) if level.isupper()]
                )
            )
        logger.setLevel(level)


@contextmanager
def set_temporary_level(new_level):
    """
    Sets a temporary log level for the global logger.

    Args:
        new_level: The log level to set temporarily.

    """

    global logger
    old_level = logger.level
    logger.setLevel(new_level)
    try:
        yield
    finally:
        logger.setLevel(old_level)


def get_log_level():
    """
    Returns the current log level of the global logger or None if the logger is not set up.
    """
    global logger
    if logger:
        return logging.getLevelName(logger.level)
    return None


# Alias functions for setting specific log levels
def set_log_level_debug():
    """Sets the log level to DEBUG."""
    set_log_level(logging.DEBUG)


def set_log_level_info():
    """Sets the log level to INFO."""
    set_log_level(logging.INFO)


def set_log_level_warning():
    """Sets the log level to WARNING."""
    set_log_level(logging.WARNING)


def set_log_level_error():
    """Sets the log level to ERROR."""
    set_log_level(logging.ERROR)


def set_log_level_critical():
    """Sets the log level to CRITICAL."""
    set_log_level(logging.CRITICAL)


# Functions to set output to console or file
def set_output_to_console():
    """Sets the output of the global logger instance to console."""
    set_default_handler(logging.StreamHandler())


def set_output_to_file(file_path):
    """Sets the output of the global logger instance to a file."""
    set_default_handler(logging.FileHandler(file_path))


def set_output_to_database(db_filename):
    """Sets the output of the global logger instance to a database."""
    set_default_handler(DatabaseHandler(db_filename))


def add_output_to_console():
    """Adds a console handler to the global logger instance."""
    logger.addHandler(logging.StreamHandler())


def add_output_to_file(file_path):
    """
    Adds a file handler to the global logger instance.

    Args:
        file_path: The path to the log file.

    """
    logger.addHandler(logging.FileHandler(file_path))


def add_output_to_database(db_filename, log_name=None, formatter=None):
    """
    Adds a database handler to the global logger instance.

    Args:
        db_filename: The filename of the SQLite database.
        log_name: The name of the log table in the database. Defaults to the name of the current file.
        formatter: The formatter to use for the log records. Defaults to a simple formatter.
    """
    logger.addHandler(DatabaseHandler(db_filename, log_name, formatter))


# Set up the logger immediately when the module is imported
setup_logger()
