from _typeshed import Incomplete as Incomplete
from typing import List, TypedDict

class MatchingFilesDict(TypedDict):
    total_files: int
    returned_files: int
    excluded_files: int
    access_denied_files: int
    errors_files: int
    files: List[str]

def check_access(file_path, access_type) -> None: ...
def get_files(path, include_pattern: Incomplete | None = ..., exclude_patterns: Incomplete | None = ..., max_depth: int = ..., follow_symlinks: bool = ..., access_type: str = ...) -> MatchingFilesDict: ...
def format_output(result, output_format) -> None: ...
def pretty_print_json(data) -> None: ...
def find_root_module(path) -> str: ...
def main() -> None: ...