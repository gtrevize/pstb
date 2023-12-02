from typing import TypedDict

class FileDetailsDict(TypedDict):
    file_path: str
    file_real_path: str
    file_name: str
    file_extension: str
    file_size: int
    file_access: str
    file_modified: float
    file_created: float
    file_owner: int
    file_group: int
    file_permissions: str

class MatchingFilesDict(TypedDict):
    total_files: int
    returned_files: int
    excluded_files: int
    access_denied_files: int
    errors_found: int
    max_depth: int
    actual_depth: int
    files: list[FileDetailsDict]

def check_access(file_path: str, access_type: str): ...
def get_files(path: str | None, include_pattern: str | None = ..., exclude_patterns: str | None = ..., max_depth: int = ..., follow_symlinks: bool = ..., access_type: str = ...): ...
def get_file_details(file_path: str) -> FileDetailsDict: ...
def format_output(result: MatchingFilesDict, output_format: str = ...) -> str: ...
def find_root_module(module): ...
def main() -> None: ...
