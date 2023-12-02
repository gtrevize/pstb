from typing import List, TypedDict

from _typeshed import Incomplete

class MatchingFilesDict(TypedDict):
    total_files: int
    returned_files: int
    excluded_files: int
    access_denied_files: int
    errors_files: int
    files: List[str]  # Assuming the list contains file names as strings

def check_access(file_path, access_type): ...
def get_files(
    path,
    include_pattern: Incomplete | None = ...,
    exclude_patterns: Incomplete | None = ...,
    max_depth: int = ...,
    follow_symlinks: bool = ...,
    access_type: str = ...,
) -> MatchingFilesDict: ...
def format_output(result, output_format): ...
def pretty_print_json(data) -> None: ...
def find_root_module(path) -> str: ...
def main() -> None: ...
