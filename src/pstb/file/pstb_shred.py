"""
dod522022m_shredder.py - DoD 5220.22-M Secure File Shredder

This module provides a Python implementation of secure file shredding based on the DoD 5220.22-M standard.
It allows you to securely overwrite and delete sensitive files, following either the 3-pass or 7-pass standard.

Usage:
1. Import the module.
2. Call the dod522022m_shred function with the appropriate parameters to securely shred a file.

Example usage:
    file_to_shred = 'path/to/your/file.txt'
    true_random = True  # Set to True to use true random numbers, False for pseudo-random
    standard = "3-pass"  # Choose "3-pass" or "7-pass"
    adaptive = True  # Set to True to find the best block size automatically
    dod522022m_shred(file_to_shred, block_size=None, true_random=true_random, standard=standard, adaptive=adaptive)

Functions:
- dod522022m_shred(file_path, block_size=None, true_random=False, standard="3-pass", adaptive=True):
    Securely shreds a file according to DoD 5220.22-M standard.

- overwrite_with_pattern(file, pattern, block_size):
    Overwrites the content of a file with a given pattern.

- verify_pass(file_path, expected_pattern, block_size):
    Verifies that the content of a file matches the expected pattern.

- generate_random_string(length):
    Generates a random string of alphanumeric characters.

- fetch_true_random_numbers(block_size, timeout=5):
    Fetches true random numbers from random.org or falls back to pseudo-random numbers.
"""
import os
import random
import string

import requests
from tbx.file.speed import find_best_block_size


def overwrite_with_pattern(file, pattern, block_size):
    """
    Overwrites the content of a file with a given pattern.

    Args:
        file (file): The file to overwrite.
        pattern (bytes): The pattern to write.
        block_size (int): The block size for reading and writing.

    Returns:
        None
    """
    while True:
        data = file.read(block_size)
        if not data:
            break
        file.write(pattern * len(data))


def verify_pass(file_path, expected_pattern, block_size):
    """
    Verifies that the content of a file matches the expected pattern.

    Args:
        file_path (str): The path to the file to verify.
        expected_pattern (bytes): The expected pattern to compare.
        block_size (int): The block size for reading.

    Returns:
        bool: True if the file content matches the expected pattern, False otherwise.
    """
    with open(file_path, "rb") as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            if data != expected_pattern * len(data):
                return False
    return True


def dod522022m_shred(
    file_path, block_size=None, true_random=False, standard="3-pass", adaptive=True
):
    """
    Securely shreds a file according to DoD 5220.22-M standard.

    Args:
        file_path (str): The path to the file to be shredded.
        block_size (int, optional): The block size for reading and writing. If None, it will be determined adaptively.
        true_random (bool, optional): Whether to use true random numbers for overwriting. Default is False (pseudo-random).
        standard (str, optional): The DoD standard to follow, either "3-pass" or "7-pass". Default is "3-pass".
        adaptive (bool, optional): Whether to adaptively determine the block size based on speed. Default is True.

    Returns:
        None
    """
    # Validate the 'standard' parameter
    if standard not in ["3-pass", "7-pass"]:
        raise ValueError(
            "Invalid value for 'standard' parameter. It must be '3-pass' or '7-pass'."
        )

    # If 'block_size' is not specified and 'adaptive' is True, find the best block size
    if block_size is None and adaptive:
        block_size = find_best_block_size(file_path)
        print(f"Selected block size for shredding: {block_size} bytes")

    # Generate two random file names
    new_file_name_1 = generate_random_string(16) + os.path.splitext(file_path)[1]
    new_file_name_2 = generate_random_string(16) + os.path.splitext(file_path)[1]

    # Passes (3-pass mode)
    passes = 3 if standard == "3-pass" else 7

    for pass_num in range(passes):
        with open(file_path, "rb+") as file:
            if true_random:
                pattern = fetch_true_random_numbers(block_size)
            else:
                if pass_num == 0:
                    pattern = b"\x00"  # Pass 1: Overwrite with all zeros (0x00)
                elif pass_num == 1:
                    pattern = b"\xFF"  # Pass 2: Overwrite with all ones (0xFF)
                else:
                    pattern = bytes(
                        [random.randint(0, 255) for _ in range(block_size)]
                    )  # Pass 3-7: Random data
            overwrite_with_pattern(file, pattern, block_size)

        # Verify pass
        if pass_num < passes - 1:  # Skip verification after the last pass
            if not verify_pass(file_path, pattern, block_size):
                print(f"Pass {pass_num + 1} verification failed.")
                return

    # Rename the file to a random name (1st rename)
    os.rename(file_path, new_file_name_1)

    # Securely delete the file by truncating it and removing it from the file system
    with open(new_file_name_1, "rb+") as file:
        file.truncate()
    os.remove(new_file_name_1)


# Usage
file_to_shred = "path/to/your/file.txt"
true_random = True  # Set to True to use true random numbers, False for pseudo-random
standard = "3-pass"  # Choose "3-pass" or "7-pass"
adaptive = True  # Set to True to find the best block size automatically
dod522022m_shred(
    file_to_shred,
    block_size=None,
    true_random=true_random,
    standard=standard,
    adaptive=adaptive,
)
