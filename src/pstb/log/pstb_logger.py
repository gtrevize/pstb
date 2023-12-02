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
import contextlib
import logging
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import colorlog
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global variable to hold the logger instance, initialized to None because the logger is set up in setup_logger()
logger: logging.Logger = None  # type: ignore

#######################
# Constants definitions
#######################

# Tuple of integers of valid log levels for use in the set_log_level function
_VALID_LOG_LEVELS = (0, 10, 20, 30, 40, 50)  # NOTSET  # DEBUG  # INFO  # WARNING  # ERROR  # CRITICAL
_VALID_LOG_LEVELS_STR = ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
_VALID_LOG_LEVELS_DICT = dict(zip(_VALID_LOG_LEVELS_STR, _VALID_LOG_LEVELS))

_LOG_COLORS = {"DEBUG": "cyan", "INFO": "green", "WARNING": "yellow", "ERROR": "red", "CRITICAL": "red,bg_white"}

_FORMAT_STR = "{levelname:8s} {module:20s}:{funcName:20s}:{lineno:4d} - {message}"
_FORMAT_COLOR_STR = "{log_color}{levelname:8s} {module:20s}:{funcName:20s}:{lineno:4d} - {reset}{message}"

_MAX_REPETITIONS = 3

#####################
# Classes definitions
#####################


class DatabaseHandler(logging.Handler):
    """
    Creates a handler that writes log records to a SQLite database.
    The database filename can be specified as an argument or read from the PYTHON_LOG_DATABASE environment variable.
    The default filename is the name of the current file with a _log.db suffix and extension.
    Registers a function to close the database when the program exits.

    Args:
        db_filename: The filename of the SQLite database. Defaults to the value of the PYTHON_LOG_DATABASE environment
            variable or the name of the current file with a _log.db suffix and extension.
        dont_create: If True, the database file must already exist. Defaults to False.
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

    _db_filename: str
    _log_name: str
    _dont_create: bool = False

    def __init__(self, db_filename: str | None = None, dont_create=False, log_name: str | None = None, formatter=None):
        super().__init__()
        self.db_filename = str(db_filename)

        # Set the log name if not specified default to the name of the current file
        if log_name:
            self._log_name = log_name
        else:
            self._log_name = Path(sys.argv[0]).resolve().stem

        # Set the formatter if specified otherwise use the default formatter
        if formatter is not None:
            self.setFormatter(formatter)
        else:
            # Default formatter
            self.setFormatter(logging.Formatter(_FORMAT_STR, style="{"))

        self.connect_to_database(dont_create=dont_create)

        # Register a function to close the database when the program exits
        atexit.register(self.close)

    def connect_to_database(self, dont_create=False):
        """
        Connects to the SQLite database specified in the db_filename property.

        Args:
            dont_create: If True, the database file must already exist. Defaults to False.

        Raises:
            FileNotFoundError: If dont_create is True and the database file does not exist.
        """

        if dont_create and not os.path.exists(self.db_filename):
            raise FileNotFoundError(f"Database file '{self.db_filename}' does not exist")

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
            f"""
            INSERT INTO {self.log_name} (timestamp, module, funcName, lineno, level, message,
                exception, formatted_message)
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
    def db_filename(self, db_filename):
        """
        Sets the database filename and connects to the database.
        If a full path is not specified, the database filename is assumed to be in the log directory.
        The log directory is read from the PYTHON_LOG_DIR environment variable or defaults to the
            {application root}/logs subdirectory.
        The database filename is read from the PYTHON_LOG_DATABASE environment variable or defaults to the
            name of the current file with a _log.db suffix and extension.
        The PYTHON_APP_ROOT_DIR environment variable can be used to specify the application root directory.
        If the path to the database file does not exist, it will be created,
            including all the intermediate directories.

        Args:
            db_filename: The filename of the SQLite database.

        Raises:
            FileNotFoundError: If the database file does not exist.
        """
        app_dir_name, _ = os.path.split(sys.argv[0])
        app_root_dir = os.getenv("PYTHON_APP_ROOT_DIR", app_dir_name)
        log_root_dir = os.getenv("PYTHON_LOG_DIR", Path(app_root_dir) / "logs")
        if not db_filename:
            db_filename = os.getenv("PYTHON_LOG_DATABASE", f"{log_root_dir}_log.db")

        if not os.path.dirname(db_filename):
            db_filename = os.path.join(log_root_dir, db_filename)

        if not os.path.exists(os.path.dirname(db_filename)):
            os.makedirs(os.path.dirname(db_filename), exist_ok=True)

        self._db_filename = db_filename


class SuppressRepeatFilter(logging.Filter):
    """
    Suppresses repeated log messages.
    If a log message is repeated more than the maximum number of repetitions, the message is suppressed.
    Reads the maximum number of repetitions from the PYTHON_LOG_MAX_REPETITIONS environment variable or uses the
    default value of 3.

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
            max_repetitions = int(os.getenv("PYTHON_LOG_MAX_REPETITIONS", _MAX_REPETITIONS))
        self.max_repetitions = max_repetitions

    def filter(self, record):
        current_log = record.msg
        if current_log == self._last_log:
            self._repeat_count += 1
            # Start suppressing after exceeding maximum repetitions
            return self._repeat_count < self._max_repetitions
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
    def max_repetitions(self, max_repetitions):
        if max_repetitions < 1:
            raise ValueError("Maximum repetitions must be a positive integer")
        self._max_repetitions = max_repetitions


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
    log_name = os.getenv("PYTHON_LOG_NAME", Path(__file__).resolve().stem)
    logger = logging.getLogger(log_name)

    # Read log level from environment variable or use default
    log_level = os.getenv("PYTHON_LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Read log output from environment variable
    log_output = os.getenv("PYTHON_LOG_OUTPUT", "console").lower()

    # Set default handler based on the environment variable
    # TODO: Add support for filename and path checking and creation if needed
    if log_output == "file":
        log_file = os.getenv("PYTHON_LOG_FILE", f"{Path(__file__).resolve().with_suffix('')}.log")
        set_default_handler(logging.FileHandler(log_file))
    elif log_output == "database":
        db_filename = os.getenv("PYTHON_LOG_DATABASE", f"{Path(__file__).resolve().with_suffix('')}.db")
        set_default_handler(DatabaseHandler(db_filename=db_filename))
    else:
        set_default_handler(logging.StreamHandler())

    # Set the default initial formatter
    set_log_formatter()

    return logger


def set_default_handler(handler):
    """
    Sets the default handler for the global logger instance.
    Uses a color formatter for console output.
    Removes all existing handlers and adds the new handler to the logger.

    Args:
        handler: The handler to set as the default handler.
    """

    global logger
    if logger:
        # Remove all existing handlers
        logger.handlers.clear()

        # Add the handler to the logger
        logger.addHandler(handler)


def set_log_formatter(format_str=_FORMAT_COLOR_STR, colorize=True, log_colors=_LOG_COLORS):
    """
    Sets the formatter for the global logger instance.
    Supports colorized output for console output and will automatically set the formatter for all existing handlers.
    Colorized will be applied only to the handlers that support it. For example, the StreamHandler supports it.

    Args:
        format_str: The format string to use for the formatter. Defaults to _FORMAT_COLOR_STR.
            It uses the new style string formatting with curly braces {} instead of ()%.
        colorize: If True, colorize the output. Defaults to True.
        log_colors: A dictionary of log colors. Defaults to _LOG_COLORS.
    """

    global logger
    if logger:
        if colorize:
            # Create a formatter with color support
            formatter = colorlog.ColoredFormatter(_FORMAT_COLOR_STR, style="{", log_colors=log_colors)
        else:
            # Create a simple formatter
            formatter = logging.Formatter(_FORMAT_STR, style="{")

        # Set the new formatter for all existing handlers that support it. For example, the StreamHandler supports it.
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(formatter)


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
        if level not in _VALID_LOG_LEVELS:
            raise ValueError(
                f"'{level}' is not a valid logging level. Valid logging levels are {_VALID_LOG_LEVELS_DICT}"
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
        return logger.level
    return None


def get_log_level_name():
    """
    Returns the current log level name of the global logger or None if the logger is not set up.
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


# FIXME: Fix it. These functions are not working properly. They are not flushing the output.
def unbuffered_console_output(stream=sys.stdout):
    """
    Temporary changes the console output to unbuffered mode.

    Args:
        stream_name: The name of the stream to change. Must be either 'stdout' or 'stderr'.
        Defaults to 'stdout'.

    Raises:
        ValueError: If the stream name is not 'stdout' or 'stderr'.
    """

    # Save the original stream
    original_stream = stream
    unbuffered_stream = os.fdopen(original_stream.fileno(), "w", buffering=1)

    # Replace the original stream with the unbuffered stream
    if stream is sys.stdout:
        sys.stdout = unbuffered_stream
    elif stream is sys.stderr:
        sys.stderr = unbuffered_stream
    else:
        raise ValueError("Only sys.stdout and sys.stderr are supported")

    try:
        yield
    finally:
        # Flush and close the unbuffered stream
        unbuffered_stream.flush()
        # unbuffered_stream.close()

        # Restore the original stream
        if stream is sys.stdout:
            sys.stdout = original_stream
        elif stream is sys.stderr:
            sys.stderr = original_stream


# FIXME: Fix it. It doesn't work. It needs to support __enter__ and __exit__ methods, and yield the file object.
@contextlib.contextmanager
def unbuffered_file_output(file_path):
    """
    Temporary changes the file output to unbuffered mode.

    Args:
        file_path: The path to the file to change.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    # Open the original file with unbuffered writing
    original_file = open(file_path, "w", buffering=1)

    try:
        yield original_file
    finally:
        # Close the file to ensure all data is written
        original_file.close()


def set_output_to_console():
    """Sets the output of the global logger instance to console."""
    set_default_handler(logging.StreamHandler(sys.stdout))


def set_output_to_file(file_path, dont_create=False):
    """
    Sets the output of the global logger instance to a file.

    Args:
        file_path: The path to the log file.
        dont_create: If True, the file must already exist. Defaults to False.

    Raises:
        FileNotFoundError: If dont_create is True and the file does not exist.
    """

    if dont_create and not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist, and dont_create is True")
    set_default_handler(logging.FileHandler(file_path))


def set_output_to_database(db_filename, dont_create=False):
    """
    Sets the output of the global logger instance to a database.

    Args:
        db_filename: The filename of the SQLite database.
        dont_create: If True, the database file must already exist. Defaults to False.

    Raises:
        FileNotFoundError: If the database file does not exist.
    """
    set_default_handler(DatabaseHandler(db_filename, dont_create=dont_create))


def add_output_to_console():
    """Adds a console handler to the global logger instance."""
    logger.addHandler(logging.StreamHandler())


def add_output_to_file(file_path, dont_create=False):
    """
    Adds a file handler to the global logger instance.

    Args:
        file_path: The path to the log file.
        dont_create: If True, the file must already exist. Defaults to False.

    Raises:
        FileNotFoundError: If dont_create is True and the file does not exist.
    """

    if dont_create and not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist, and dont_create is True")
    logger.addHandler(logging.FileHandler(file_path))


def add_output_to_database(db_filename, dont_create=False, log_name="", formatter=""):
    """
    Adds a database handler to the global logger instance.

    Args:
        db_filename: The filename of the SQLite database.
        dont_create: If True, the database file must already exist. Defaults to False.
        log_name: The name of the log table in the database. Defaults to the name of the current file.
        formatter: The formatter to use for the log records. Defaults to a simple formatter.
    """
    logger.addHandler(DatabaseHandler(db_filename, dont_create=dont_create, log_name=log_name, formatter=formatter))


# Set up the logger immediately when the module is imported
setup_logger()
