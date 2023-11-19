"""
file_utilities.py - File Utilities Module

This module provides utility functions for working with files and directories, including file access checks,
recursive file retrieval, and access control.

Functions:
- check_access(file_path, access_type):
    Checks if a file has the specified access type.

- get_files(path, include_pattern=None, exclude_patterns=None, max_depth=0, follow_symlinks=False, access_type="r"):
    Recursively retrieves a list of files in a directory based on include/exclude patterns and access type.

    Returns a dictionary with the following format:
    {
        "total_files": number,
        "returned_files": number,
        "excluded_files": number,
        "access_denied_files": number,
        "errors_files": number,
        "files": [list of files]
    }
    
    - total_files: Total number of files encountered during the search.
    - returned_files: Number of files that meet the specified access type and pattern criteria.
    - excluded_files: Number of files excluded based on patterns.
    - access_denied_files: Number of files denied access based on permissions.
    - errors_files: Number of files with errors encountered during the search.
    - files: List of file paths that meet the specified access type and pattern criteria.

- pretty_print_json(data):
    Pretty-prints JSON data with indentation and colored output.

- format_output(result, output_format):
    Formats the result based on the specified output format.

- main():
    The command-line entry point for the File Utilities Command-Line Utility. Accepts various arguments to control file retrieval, access checks, and output format.

Usage:
To run this module as a command-line utility, execute it with the desired command-line arguments. Use the "--help" option to display usage information.
"""


import argparse
import fnmatch
import json
import os

from colorama import Fore, init
from tabulate import tabulate

# Initialize colorama for colored output (Windows support)
init()


def check_access(file_path, access_type):
    """
    Checks if a file has the specified access type.

    Args:
        file_path (str): The path to the file.
        access_type (str): Access type to check. "r" for reading, "w" for writing, "rw" for both.

    Returns:
        bool: True if the file has the specified access type, False otherwise.
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
    path,
    include_pattern=None,
    exclude_patterns=None,
    max_depth=0,
    follow_symlinks=False,
    access_type="r",
):
    """
    Recursively retrieves a list of files in a directory based on include/exclude patterns and access type.

    Args:
        path (str): The path to the directory or file to start searching from.
        include_pattern (str, optional): Pattern to include files (e.g., '*.txt'). Default is None (include all).
        exclude_patterns (list of str, optional): List of patterns to exclude files (e.g., ['*.jpg', '*.png']).
            Default is None (no exclusions).
        max_depth (int, optional): Maximum depth of recursion. Default is 0 (infinite).
        follow_symlinks (bool, optional): Whether to follow symbolic links. Default is False.
        access_type (str, optional): Access type to check for each file. "r" for reading, "w" for writing, "rw" for both.
            Default is "r".

    Returns:
        dict: A dictionary containing file information as specified.
    """
    matching_files = {
        "total_files": 0,
        "returned_files": 0,
        "excluded_files": 0,
        "access_denied_files": 0,
        "errors_files": 0,
        "files": [],
    }

    if os.path.isfile(path) and check_access(path, access_type):
        matching_files["total_files"] = 1
        matching_files["returned_files"] = 1
        matching_files["files"].append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path, followlinks=follow_symlinks):
            current_depth = root[len(path) :].count(os.path.sep)
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
                        if not any(
                            fnmatch.fnmatch(f, pattern) for pattern in exclude_patterns
                        )
                    ]

                matching_files["total_files"] += len(files)
                matching_files["excluded_files"] += len(files) - len(files_to_include)

                # Check access and add to the list if allowed
                for file_name in files_to_include:
                    file_path = os.path.join(root, file_name)
                    matching_files["total_files"] += 1
                    if check_access(file_path, access_type):
                        matching_files["returned_files"] += 1
                        matching_files["files"].append(file_path)
                    else:
                        matching_files["access_denied_files"] += 1

    return matching_files


def format_output(result, output_format):
    if output_format == "plain":
        return result
    elif output_format == "text":
        return tabulate(result.items(), tablefmt="grid")
    elif output_format == "json":
        return json.dumps(result, indent=4)
    elif output_format == "csv":
        csv_result = result.copy()
        csv_result["files"] = "\n".join(csv_result["files"])
        return csv_result
    elif output_format == "html":
        html_result = tabulate(result.items(), tablefmt="html")
        return html_result
    elif output_format == "json-pretty":
        return pretty_print_json(json.dumps(result, indent=4))


def pretty_print_json(data):
    formatted_json = json.dumps(data, indent=4)
    colored_json = Fore.BLUE + formatted_json + Fore.RESET

    print(colored_json)


def main():
    parser = argparse.ArgumentParser(description="File Utilities Command-Line Utility")
    parser.add_argument(
        "path", help="The path to the directory or file to start searching from."
    )
    parser.add_argument(
        "-i",
        "--include-pattern",
        help="Pattern to include files (e.g., '*.txt'). Default is None (include all).",
    )
    parser.add_argument(
        "-e",
        "--exclude-patterns",
        nargs="+",
        help="List of patterns to exclude files (e.g., '*.jpg' '*.png'). Default is None (no exclusions).",
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
    parser.add_argument(
        "-o", "--output", help="Output file name. Writes to stdout if not specified."
    )

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

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
