import logging
from _typeshed import Incomplete
from collections.abc import Generator
from math import log as log

logger: logging.Logger

class DatabaseHandler(logging.Handler):
    def __init__(self, db_filename: str = ..., dont_create: bool = ..., log_name: str = ..., formatter: Incomplete | None = ...) -> None: ...
    conn: Incomplete
    cursor: Incomplete
    def connect_to_database(self, dont_create: bool = ...) -> None: ...
    def emit(self, record) -> None: ...
    def close(self) -> None: ...
    @property
    def log_name(self): ...
    @log_name.setter
    def log_name(self, name) -> None: ...
    @property
    def db_filename(self): ...
    @db_filename.setter
    def db_filename(self, db_filename) -> None: ...

class SuppressRepeatFilter(logging.Filter):
    def __init__(self, max_repetitions: Incomplete | None = ...) -> None: ...
    def filter(self, record): ...
    @property
    def max_repetitions(self): ...
    @max_repetitions.setter
    def max_repetitions(self, repetitions) -> None: ...

def setup_logger(): ...
def set_default_handler(handler) -> None: ...
def set_log_formatter(format_str=..., colorize: bool = ..., log_colors=...) -> None: ...
def set_log_level(level) -> None: ...
def set_temporary_level(new_level) -> Generator[None, None, None]: ...
def get_log_level(): ...
def get_log_level_name(): ...
def set_log_level_debug() -> None: ...
def set_log_level_info() -> None: ...
def set_log_level_warning() -> None: ...
def set_log_level_error() -> None: ...
def set_log_level_critical() -> None: ...
def unbuffered_console_output(stream=...) -> Generator[None, None, None]: ...
def unbuffered_file_output(file_path) -> Generator[Incomplete, None, None]: ...
def set_output_to_console() -> None: ...
def set_output_to_file(file_path, buffered: bool = ...) -> None: ...
def set_output_to_database(db_filename) -> None: ...
def add_output_to_console() -> None: ...
def add_output_to_file(file_path) -> None: ...
def add_output_to_database(db_filename, dont_create: bool = ..., log_name: str = ..., formatter: str = ...) -> None: ...
