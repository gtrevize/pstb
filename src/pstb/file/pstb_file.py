"""
file_utilities.py - File Utilities Module

This module provides utility functions for working with files and directories, including file access checks,
recursive file retrieval, and access control.

Functions:
    check_access(file_path, access_type):
        Checks if a file has the specified access type.

    get_files(path, include_pattern=None, exclude_patterns=None, max_depth=0, follow_symlinks=False, access_type="r"):
        Recursively retrieves a list of files in a directory based on include/exclude patterns and access type.

    format_output(result, output_format):
        Formats the result based on the specified output format.

    find_root_module(module):
        Finds the root directory of a given module.

More information about the functions can be found in their docstrings.
"""


import argparse
import fnmatch
import json
import os
import sys
from typing import TypedDict

from tabulate import tabulate

# Add the src directory to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")))

from pstb.console.pstb_console import pretty_json  # noqa: E402
from pstb.string.pstb_string import dict_to_csv_str, dict_to_html_str  # noqa: E402

#############
# Type hints
#############


class FileDetailsDict(TypedDict):
    """Type hint for the dictionary returned by get_file_details."""

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
    """Type hint for the dictionary returned by get_files."""

    total_files: int
    returned_files: int
    excluded_files: int
    access_denied_files: int
    errors_found: int
    max_depth: int  # Maximum depth of recursion allowed
    actual_depth: int  # Actual depth of recursion used
    files: list[FileDetailsDict]  # List of files that meet the specified access type and pattern criteria


###########
# Functions
###########


def check_access(file_path: str, access_type: str):
    """
    Checks if a file has the specified access type.

    Args:
        file_path (str): The path to the file.
        access_type (str): Access type to check. "r" for reading, "w" for writing, "rw" for both.

    Returns:
        bool: True if the file has the specified access type, False otherwise.

    Example:
        >>> check_access("my_file.txt", "r")
        True
    """
    try:
        if access_type == "r":
            return os.access(file_path, os.R_OK)
        elif access_type == "w":
            return os.access(file_path, os.W_OK)
        elif access_type == "rw":
            return os.access(file_path, os.R_OK) and os.access(file_path, os.W_OK)
        else:
            return False
    except (PermissionError, FileNotFoundError):
        # Handle permission errors or missing files by returning False
        return False


def get_files(
    path: str | None,
    include_pattern: str | None = None,
    exclude_patterns: str | None = None,
    max_depth: int = 0,
    follow_symlinks: bool = False,
    access_type: str = "r",
):
    """
    Recursively retrieves a list of files in a directory based on include/exclude patterns and access type.

    Args:
        path (str): The path to the directory or file to start searching from.
        include_pattern (str, optional): Pattern to include files (e.g., '\\*.txt'). Default is None (include all).
        exclude_patterns (list of str, optional): List of patterns to exclude files (e.g., ['\\*.jpg', '\\*.png']).
            Default is None (no exclusions).
        max_depth (int, optional): Maximum depth of recursion. Default is 0 (infinite).
        follow_symlinks (bool, optional): Whether to follow symbolic links. Default is False.
        access_type (str, optional): Access type to check for each file. "r" for reading, "w" for writing, "rw"
            for both. Default is "r".

    Raises:
        ValueError: If the path is invalid.

    Returns:
        dict: A dictionary containing file information as specified.
    """
    matching_files: MatchingFilesDict = {
        "total_files": 0,
        "returned_files": 0,
        "excluded_files": 0,
        "access_denied_files": 0,
        "max_depth": max_depth,
        "actual_depth": 0,
        "errors_found": 0,
        "files": [],
    }

    if not path:
        path = os.getcwd()

    actual_depth = 0

    if os.path.isfile(path) and check_access(path, access_type):
        matching_files["total_files"] = 1
        matching_files["returned_files"] = 1
        matching_files["files"].append(get_file_details(path))
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path, followlinks=follow_symlinks):
            current_depth = root[len(path) :].count(os.path.sep)  # noqa: E203
            if current_depth > actual_depth:
                actual_depth = current_depth
            if max_depth == 0 or current_depth <= max_depth:
                # Include files based on patterns (include takes precedence over exclude)
                if include_pattern is not None:
                    files_to_include = fnmatch.filter(files, include_pattern)
                else:
                    files_to_include = files

                # Exclude files based on patterns
                if exclude_patterns is not None:
                    files_to_include = [
                        f
                        for f in files_to_include
                        if not any(fnmatch.fnmatch(f, pattern) for pattern in exclude_patterns)
                    ]

                matching_files["total_files"] += len(files)
                matching_files["excluded_files"] += len(files) - len(files_to_include)

                # Check access and add to the list if allowed
                for file_name in files_to_include:
                    file_path = os.path.join(root, file_name)
                    matching_files["total_files"] += 1
                    if check_access(file_path, access_type):
                        matching_files["returned_files"] += 1
                        matching_files["files"].append(get_file_details(file_path))
                    else:
                        matching_files["access_denied_files"] += 1
    else:
        raise ValueError(f"Invalid path: '{path}'")

    matching_files["actual_depth"] = actual_depth

    return matching_files


def get_file_details(file_path: str) -> FileDetailsDict:
    """
    Gets details about a file.

    Args:
        file_path (str): The path to the file.

    Raises:
        OSError: If the file doesn't exist or is inaccessible.
        FileNotFoundError: If the file doesn't exist or is inaccessible.
        PermissionError: If access to the file is denied.

    Returns:
        dict: A dictionary containing the following file details:
            - file_path: The full path to the file.
            - file_reaL_path: The full real path to the file, after resolving any symbolic links.
            - file_name: The name of the file.
            - file_extension: The extension of the file.
            - file_size: The size of the file in bytes.
            - file_access: The access type of the file ("r", "w", "x", or a combination of those).
            - file_modified: The date and time the file was last modified.
            - file_created: The date and time the file was created.
            - file_owner: The owner of the file.
            - file_group: The group of the file.
            - file_permissions: The permissions of the file.
    """
    result: FileDetailsDict = {
        "file_path": "",
        "file_real_path": "",
        "file_name": "",
        "file_extension": "",
        "file_size": 0,
        "file_access": "",
        "file_modified": 0,
        "file_created": 0,
        "file_owner": 0,
        "file_group": 0,
        "file_permissions": "",
    }

    try:
        result["file_name"] = os.path.basename(file_path)
        result["file_path"] = os.path.splitext(file_path)[0]
        result["file_real_path"] = os.path.realpath(file_path)
        result["file_extension"] = os.path.splitext(file_path)[1]
        if os.access(file_path, os.R_OK):
            result["file_access"] += "r"
        if os.access(file_path, os.W_OK):
            result["file_access"] += "w"
        if os.access(file_path, os.X_OK):
            result["file_access"] += "x"
    except FileNotFoundError:
        raise OSError(f"File '{file_path}' doesn't exist or is inaccessible")
    except PermissionError:
        raise OSError(f"Access denied to file '{file_path}'")

    try:
        result["file_size"] = os.path.getsize(file_path)
        result["file_modified"] = os.path.getmtime(file_path)
        result["file_created"] = os.path.getctime(file_path)
        result["file_owner"] = os.stat(file_path).st_uid
        result["file_group"] = os.stat(file_path).st_gid
        result["file_permissions"] = oct(os.stat(file_path).st_mode & 0o777)
    except OSError:
        raise OSError(f"Unable to get file details for '{file_path}'")

    return result


def format_output(result: MatchingFilesDict, output_format: str = "plain") -> str:
    """
    Formats the result based on the specified output format.

    Args:
        result (dict): The result to format.
        output_format (str): The output format to use. One of "plain", "text", "json", "csv", "html", "json-pretty".
            text: Tabular output using the tabulate library.
            csv: Only the "files" key is formatted as a string with newline characters separating the file paths.
            pretty-json: JSON output with indentation and colored output, using the colorama library.

    Raises:
        ValueError: If the output format is not one of the valid options.

    Returns:
        str: The formatted result.
    """

    if output_format == "plain":
        return str(result)
    elif output_format == "text":
        return tabulate(result.items(), tablefmt="grid")
    elif output_format == "json":
        return json.dumps(result, indent=4)
    elif output_format == "csv":
        result_files: list = list(result["files"])  # conversion to list is required for mypy
        return dict_to_csv_str(result_files)
    elif output_format == "html":
        return dict_to_html_str(
            dict(result)
        )  # Convert to a regular dict before passing to dict_to_html_str to avoid type error
    elif output_format == "json-pretty":
        return pretty_json(dict(result))  # Convert to a regular dict before passing to pretty_json to avoid type error
    else:
        raise ValueError(f"Invalid output format: {output_format}. Valid formats are: plain, text, json, csv, html")


def find_root_module(module):
    """
    Finds the root directory of a given module.

    This function navigates up the directory tree of the provided module's file path until
    it reaches a directory without an `__init__.py` file, which is typically the root of
    the package. The root directory is then returned.

    Args:
        module (ModuleType): The module for which to find the root directory. This should
            be a reference to the module, not the module's name as a string.

    Returns:
        str: The file path representing the root directory of the module's package.
            If the module is not part of a package, the directory containing the module file is returned.

    Example:
        >>> root_path = find_root_module(my_library)
        >>> print("Root path of the library:", root_path)
    """
    # Get the file path of the module
    module_file_path = module.__file__

    # Navigate up the directory structure to find the package root
    current_path = module_file_path
    while True:
        current_path, current_dir = os.path.split(current_path)
        if not current_dir or os.path.exists(os.path.join(current_path, "__init__.py")):
            break

    return current_path


######
# Main
######


def main():
    """
    Main function for the file_utilities command-line utility.
    This function parses command-line arguments and calls the appropriate functions.
    The valid command-line arguments are as follows:

        -i, --include-pattern: Pattern to include files (e.g., '\\*.txt'). Default is None (include all).
        -e, --exclude-patterns: List of patterns to exclude files (e.g., '\\*.jpg'). Default is None (no exclusions).
        -d, --max-depth: Maximum depth of recursion. Default is 0 (infinite).
        -s, --follow-symlinks: Whether to follow symbolic links. Default is False.
        -a, --access-type: Access type to check. 'r' for reading, 'w' for writing, 'rw' for both. Default is 'r'.
        -f, --format: Output format. Default is 'plain'.
        -o, --output: Output file name. Writes to stdout if not specified.
    """

    parser = argparse.ArgumentParser(description="File Utilities Command-Line Utility")
    parser.add_argument("path", help="The path to the directory or file to start searching from.")
    parser.add_argument(
        "-i",
        "--include-pattern",
        help="Pattern to include files (e.g., '\\*.txt'). Default is None (include all).",
    )
    parser.add_argument(
        "-e",
        "--exclude-patterns",
        nargs="+",
        help="List of patterns to exclude files (e.g., '\\*.jpg'). Default is None (no exclusions).",
    )
    parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=0,
        help="Maximum depth of recursion. Default is 0 (infinite).",
    )
    parser.add_argument(
        "-s",
        "--follow-symlinks",
        action="store_true",
        help="Whether to follow symbolic links. Default is False.",
    )
    parser.add_argument(
        "-a",
        "--access-type",
        choices=["r", "w", "rw"],
        default="r",
        help="Access type to check for each file. 'r' for reading, 'w' for writing, 'rw' for both. Default is 'r'.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["plain", "text", "json", "csv", "html", "json-pretty"],
        default="plain",
        help="Output format. Default is 'plain'.",
    )
    parser.add_argument("-o", "--output", help="Output file name. Writes to stdout if not specified.")

    args = parser.parse_args()

    try:
        result = get_files(
            args.path,
            include_pattern=args.include_pattern,
            exclude_patterns=args.exclude_patterns,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            access_type=args.access_type,
        )
        formatted_output = format_output(result, args.format)

        if args.output:
            with open(args.output, "w") as output_file:
                output_file.write(formatted_output)
        else:
            print(formatted_output)

    except ValueError as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
